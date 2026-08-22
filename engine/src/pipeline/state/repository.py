"""
Typed access layer for the pipeline state store.

This is the ONLY file allowed to contain raw SQL against jobs/job_stages/
artifacts. The orchestrator (and everything else) talks to the database
exclusively through the Repository class below — never through ad hoc
queries elsewhere.

Per Phase 1, items 1.2 and 1.4.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone


def generate_job_id() -> str:
    """job_<YYYYMMDD>_<4 hex chars> — e.g. 'job_20260812_ab12'."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = secrets.token_hex(2)
    return f"job_{date_part}_{suffix}"


@dataclass
class Job:
    id: str
    source_pptx_path: str
    source_video_path: str
    review_mode: str
    status: str
    schema_version: str
    created_at: str
    updated_at: str


@dataclass
class JobStage:
    id: int
    job_id: str
    stage_name: str
    status: str
    review_status: str
    container_name: str | None
    checkpoint_data: dict = field(default_factory=dict)
    attempt_count: int = 0
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class Artifact:
    id: int
    job_id: str
    stage_name: str
    artifact_type: str
    file_path: str
    checksum: str
    created_at: str
    updated_at: str


class Repository:
    """Wraps a single sqlite3.Connection (from db.connect()) with typed methods."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ── jobs ─────────────────────────────────────────────────────────────

    def create_job(
        self,
        source_pptx_path: str,
        source_video_path: str,
        review_mode: str,
        schema_version: str = "1.0.0",
    ) -> str:
        if review_mode not in ("auto", "manual"):
            raise ValueError(f"review_mode must be 'auto' or 'manual', got {review_mode!r}")

        job_id = generate_job_id()
        self.conn.execute(
            """
            INSERT INTO jobs (id, source_pptx_path, source_video_path, review_mode, schema_version)
            VALUES (?, ?, ?, ?, ?)
            """,
            (job_id, source_pptx_path, source_video_path, review_mode, schema_version),
        )
        self.conn.commit()
        return job_id

    def get_job(self, job_id: str) -> Job | None:
        row = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return Job(**dict(row)) if row else None

    def set_job_status(self, job_id: str, status: str) -> None:
        if status not in ("in_progress", "completed", "failed"):
            raise ValueError(f"invalid job status: {status!r}")
        self.conn.execute(
            "UPDATE jobs SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, job_id),
        )
        self.conn.commit()

    def get_resumable_jobs(self) -> list[Job]:
        """Jobs that are candidates for resume: not yet completed."""
        rows = self.conn.execute(
            "SELECT * FROM jobs WHERE status IN ('in_progress', 'failed') ORDER BY created_at"
        ).fetchall()
        return [Job(**dict(r)) for r in rows]

    # ── job_stages ───────────────────────────────────────────────────────

    def _get_stage_row(self, job_id: str, stage_name: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM job_stages WHERE job_id = ? AND stage_name = ?",
            (job_id, stage_name),
        ).fetchone()

    def start_stage(
        self,
        job_id: str,
        stage_name: str,
        container_name: str | None = None,
    ) -> None:
        """
        Mark a stage as running. Creates the row on first attempt, or
        increments attempt_count on retry (per item 1.4 — max 3 attempts
        is enforced by the orchestrator, not here).
        """
        existing = self._get_stage_row(job_id, stage_name)
        if existing is None:
            self.conn.execute(
                """
                INSERT INTO job_stages
                    (job_id, stage_name, status, container_name, attempt_count, started_at)
                VALUES (?, ?, 'running', ?, 1, datetime('now'))
                """,
                (job_id, stage_name, container_name),
            )
        else:
            self.conn.execute(
                """
                UPDATE job_stages
                SET status = 'running',
                    container_name = ?,
                    attempt_count = attempt_count + 1,
                    started_at = datetime('now'),
                    error = NULL
                WHERE job_id = ? AND stage_name = ?
                """,
                (container_name, job_id, stage_name),
            )
        self.conn.commit()

    def complete_stage(
        self,
        job_id: str,
        stage_name: str,
        checkpoint_data: dict,
        review_status: str = "not_applicable",
    ) -> None:
        if review_status not in ("not_applicable", "pending", "approved", "auto_approved"):
            raise ValueError(f"invalid review_status: {review_status!r}")
        self.conn.execute(
            """
            UPDATE job_stages
            SET status = 'completed',
                checkpoint_data = ?,
                review_status = ?,
                completed_at = datetime('now'),
                error = NULL
            WHERE job_id = ? AND stage_name = ?
            """,
            (json.dumps(checkpoint_data), review_status, job_id, stage_name),
        )
        self.conn.commit()

    def fail_stage(self, job_id: str, stage_name: str, error: str) -> None:
        self.conn.execute(
            """
            UPDATE job_stages
            SET status = 'failed', error = ?, completed_at = datetime('now')
            WHERE job_id = ? AND stage_name = ?
            """,
            (error, job_id, stage_name),
        )
        self.conn.commit()

    def set_review_status(self, job_id: str, stage_name: str, review_status: str) -> None:
        if review_status not in ("not_applicable", "pending", "approved", "auto_approved"):
            raise ValueError(f"invalid review_status: {review_status!r}")
        self.conn.execute(
            "UPDATE job_stages SET review_status = ? WHERE job_id = ? AND stage_name = ?",
            (review_status, job_id, stage_name),
        )
        self.conn.commit()

    def get_stage(self, job_id: str, stage_name: str) -> JobStage | None:
        row = self._get_stage_row(job_id, stage_name)
        if row is None:
            return None
        data = dict(row)
        data["checkpoint_data"] = json.loads(data["checkpoint_data"]) if data["checkpoint_data"] else {}
        return JobStage(**data)

    def get_stages_for_job(self, job_id: str) -> list[JobStage]:
        rows = self.conn.execute(
            "SELECT * FROM job_stages WHERE job_id = ? ORDER BY id", (job_id,)
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["checkpoint_data"] = json.loads(data["checkpoint_data"]) if data["checkpoint_data"] else {}
            result.append(JobStage(**data))
        return result

    def get_last_checkpoint(self, job_id: str, stage_name: str) -> dict | None:
        """Used by resumability logic (1.4) to compare stored vs. current input checksums."""
        stage = self.get_stage(job_id, stage_name)
        if stage is None or stage.status != "completed":
            return None
        return stage.checkpoint_data

    # ── artifacts ────────────────────────────────────────────────────────

    def upsert_artifact(
        self,
        job_id: str,
        stage_name: str,
        artifact_type: str,
        file_path: str,
        checksum: str,
    ) -> None:
        """
        Insert a new artifact row, or update the existing one for this
        (job_id, stage_name, artifact_type) if the checksum changed — this
        is what makes a human-edited plan.json show up as "changed" for
        resumability (item 1.4).
        """
        existing = self.conn.execute(
            """
            SELECT id, checksum FROM artifacts
            WHERE job_id = ? AND stage_name = ? AND artifact_type = ?
            """,
            (job_id, stage_name, artifact_type),
        ).fetchone()

        if existing is None:
            self.conn.execute(
                """
                INSERT INTO artifacts (job_id, stage_name, artifact_type, file_path, checksum)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_id, stage_name, artifact_type, file_path, checksum),
            )
        elif existing["checksum"] != checksum:
            self.conn.execute(
                """
                UPDATE artifacts
                SET checksum = ?, file_path = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (checksum, file_path, existing["id"]),
            )
        self.conn.commit()

    def get_artifact(self, job_id: str, stage_name: str, artifact_type: str) -> Artifact | None:
        row = self.conn.execute(
            """
            SELECT * FROM artifacts
            WHERE job_id = ? AND stage_name = ? AND artifact_type = ?
            """,
            (job_id, stage_name, artifact_type),
        ).fetchone()
        return Artifact(**dict(row)) if row else None

    def list_artifacts(self, job_id: str, stage_name: str | None = None) -> list[Artifact]:
        if stage_name is None:
            rows = self.conn.execute(
                "SELECT * FROM artifacts WHERE job_id = ? ORDER BY id", (job_id,)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM artifacts WHERE job_id = ? AND stage_name = ? ORDER BY id",
                (job_id, stage_name),
            ).fetchall()
        return [Artifact(**dict(r)) for r in rows]
