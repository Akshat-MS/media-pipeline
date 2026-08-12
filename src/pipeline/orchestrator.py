"""
Ties together the state store (Task 3), the LXD containers (Task 4), and
the stage contract (Task 6) into an actual run loop.

Two classes:
  ContainerStageRunner — the ONLY place in the codebase that shells out to
                          `lxc exec`. Takes a StageManifest in, returns one
                          out.
  Orchestrator          — walks the dependency graph (core/registry.py),
                          decides what to run next, handles checkpoint/
                          resume, retries, and auto/manual review branching.

Per Phase 1, item 1.3: the orchestrator runs on the HOST, never inside a
container. It is the only component that talks to the state store and
issues lxc exec calls — containers themselves are dumb transformation
workers.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from pipeline.core.manifest import Artifact, StageManifest
from pipeline.core.registry import (
    STAGE_ORDER,
    get_container_for_stage,
    get_dependencies,
    is_gated_stage,
)
from pipeline.state.repository import Repository

# Backoff between retry attempts, in seconds — index 0 is the wait after
# the FIRST failure, before the second attempt.
RETRY_BACKOFF_SECONDS: list[int] = [2, 8, 32]
DEFAULT_MAX_ATTEMPTS = 3


class StageExecutionError(Exception):
    """Raised by ContainerStageRunner when a container invocation fails."""


class ContainerStageRunner:
    """
    Invokes one stage inside its container via `lxc exec`. Writes the input
    manifest to a JSON file under the job's host-side workdir, invokes the
    stage's CLI entrypoint inside the container (which sees that same file
    under /workdir via the bind mount from Task 4), then reads back the
    output manifest the stage wrote.

    _exec_fn is injectable so orchestrator logic can be tested without a
    real LXD environment — defaults to the real subprocess-based
    implementation.
    """

    def __init__(
        self,
        host_workdir_root: Path,
        container_mount_point: str = "/workdir",
        exec_fn: Callable[[list[str]], None] | None = None,
    ):
        self.host_workdir_root = host_workdir_root
        self.container_mount_point = container_mount_point
        self._exec_fn = exec_fn or self._real_exec

    @staticmethod
    def _real_exec(cmd: list[str]) -> None:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise StageExecutionError(
                f"command failed ({result.returncode}): {' '.join(cmd)}\n"
                f"stderr: {result.stderr}"
            )

    def _to_container_path(self, host_path: Path) -> str:
        rel = host_path.relative_to(self.host_workdir_root)
        return f"{self.container_mount_point}/{rel.as_posix()}"

    def run_stage(
        self,
        job_id: str,
        stage_name: str,
        container_name: str,
        input_manifest: StageManifest,
    ) -> StageManifest:
        job_dir = self.host_workdir_root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        input_path = job_dir / f"{stage_name}_input.json"
        output_path = job_dir / f"{stage_name}_output.json"
        input_path.write_text(input_manifest.model_dump_json())

        cmd = [
            "lxc", "exec", container_name, "--",
            "pipeline", "run-stage", stage_name,
            "--input", self._to_container_path(input_path),
            "--output", self._to_container_path(output_path),
        ]
        self._exec_fn(cmd)

        if not output_path.exists():
            raise StageExecutionError(
                f"stage {stage_name!r} in {container_name!r} did not produce an output file "
                f"at the expected path: {output_path}"
            )
        return StageManifest(**json.loads(output_path.read_text()))


@dataclass
class StageRunResult:
    """What happened when the orchestrator tried to advance a job by one pass."""

    outcome: str  # "completed" | "waiting_review" | "failed" | "no_ready_stages"
    stage_name: str | None = None
    detail: str = ""


class Orchestrator:
    def __init__(
        self,
        repo: Repository,
        stage_runner: ContainerStageRunner,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        self.repo = repo
        self.stage_runner = stage_runner
        self.max_attempts = max_attempts
        self._sleep = sleep_fn

    # ── Public entrypoint ────────────────────────────────────────────────

    def run_job(self, job_id: str) -> StageRunResult:
        """
        Advance a job as far as it can go in one call: runs every stage
        whose dependencies are satisfied, in STAGE_ORDER, until either the
        job completes, a manual-review gate is hit (returns without
        running further stages), or a stage fails out of retries.

        Safe to call repeatedly — this is exactly what `pipeline resume`
        and the approve-then-continue flow both do under the hood.
        """
        job = self.repo.get_job(job_id)
        if job is None:
            raise ValueError(f"no such job: {job_id!r}")

        for stage_name in STAGE_ORDER:
            if not self._is_stage_satisfied(job_id, stage_name):
                continue  # dependencies not all complete yet — skip for now

            if is_gated_stage(stage_name) and self._awaiting_manual_review(job_id, stage_name):
                # Must be checked BEFORE the up-to-date skip below: a gated
                # stage is marked status='completed' the moment its work
                # finishes, even while review_status is still 'pending' —
                # so "completed + checksums match" alone would incorrectly
                # look skippable here. Pending review always blocks first.
                return StageRunResult("waiting_review", stage_name)

            if self._stage_is_up_to_date(job_id, stage_name):
                continue  # already done, inputs unchanged — nothing to do

            result = self._run_single_stage(job_id, job.review_mode, stage_name)
            if result.outcome != "completed":
                if result.outcome == "failed":
                    self.repo.set_job_status(job_id, "failed")
                return result

        self.repo.set_job_status(job_id, "completed")
        return StageRunResult("completed")

    # ── Dependency / skip logic ──────────────────────────────────────────

    def _is_stage_satisfied(self, job_id: str, stage_name: str) -> bool:
        deps = get_dependencies(stage_name)
        if not deps:
            return True
        completed = {
            s.stage_name for s in self.repo.get_stages_for_job(job_id) if s.status == "completed"
        }
        return all(d in completed for d in deps)

    def _gather_input_manifest(self, job_id: str, stage_name: str) -> StageManifest:
        """Combine every dependency stage's artifacts into this stage's input."""
        artifacts: list[Artifact] = []
        for dep in get_dependencies(stage_name):
            for a in self.repo.list_artifacts(job_id, stage_name=dep):
                artifacts.append(Artifact(artifact_type=a.artifact_type, file_path=a.file_path, checksum=a.checksum))
        return StageManifest(stage_name=stage_name, artifacts=artifacts)

    def _stage_is_up_to_date(self, job_id: str, stage_name: str) -> bool:
        """
        True if this stage already completed AND its recorded input
        checksums still match the current inputs — i.e. nothing upstream
        has changed since it last ran (per item 1.4: this is what a
        human-edited plan.json invalidates automatically).
        """
        existing = self.repo.get_stage(job_id, stage_name)
        if existing is None or existing.status != "completed":
            return False

        stored = existing.checkpoint_data.get("input_checksums", {})
        current_manifest = self._gather_input_manifest(job_id, stage_name)
        current = {a.artifact_type: a.checksum for a in current_manifest.artifacts}
        return stored == current

    def _awaiting_manual_review(self, job_id: str, stage_name: str) -> bool:
        """True if this gated stage already ran and is sitting at 'pending' —
        i.e. it's waiting on a human, not something to (re-)run."""
        existing = self.repo.get_stage(job_id, stage_name)
        return existing is not None and existing.review_status == "pending"

    # ── Running one stage, with retry/backoff ───────────────────────────

    def _run_single_stage(self, job_id: str, review_mode: str, stage_name: str) -> StageRunResult:
        container = get_container_for_stage(stage_name)
        input_manifest = self._gather_input_manifest(job_id, stage_name)

        existing = self.repo.get_stage(job_id, stage_name)
        attempts_so_far = existing.attempt_count if existing else 0

        last_error = ""
        for attempt_num in range(attempts_so_far, self.max_attempts):
            self.repo.start_stage(job_id, stage_name, container_name=container)
            try:
                output_manifest = self.stage_runner.run_stage(
                    job_id, stage_name, container, input_manifest
                )
                break
            except StageExecutionError as e:
                last_error = str(e)
                self.repo.fail_stage(job_id, stage_name, last_error)
                if attempt_num + 1 >= self.max_attempts:
                    return StageRunResult("failed", stage_name, last_error)
                backoff = RETRY_BACKOFF_SECONDS[min(attempt_num, len(RETRY_BACKOFF_SECONDS) - 1)]
                self._sleep(backoff)
        else:
            return StageRunResult("failed", stage_name, last_error)

        review_status = self._resolve_review_status(stage_name, review_mode)

        checkpoint_data = {
            "input_checksums": {a.artifact_type: a.checksum for a in input_manifest.artifacts},
            "output_artifacts": [a.model_dump() for a in output_manifest.artifacts],
        }
        self.repo.complete_stage(job_id, stage_name, checkpoint_data, review_status=review_status)

        for artifact in output_manifest.artifacts:
            self.repo.upsert_artifact(
                job_id, stage_name, artifact.artifact_type, artifact.file_path, artifact.checksum
            )

        if is_gated_stage(stage_name) and review_status == "pending":
            return StageRunResult("waiting_review", stage_name)
        return StageRunResult("completed", stage_name)

    @staticmethod
    def _resolve_review_status(stage_name: str, review_mode: str) -> str:
        if not is_gated_stage(stage_name):
            return "not_applicable"
        return "auto_approved" if review_mode == "auto" else "pending"

    # ── Manual review approval ───────────────────────────────────────────

    def approve_current_gate(self, job_id: str) -> None:
        """
        Called by `pipeline approve <job_id>`. Finds whichever gated stage
        is currently 'pending' for this job and marks it 'approved' — the
        next run_job() call then proceeds past it.
        """
        for stage in self.repo.get_stages_for_job(job_id):
            if stage.review_status == "pending":
                self.repo.set_review_status(job_id, stage.stage_name, "approved")
                return
        raise ValueError(f"no stage is currently pending review for job {job_id!r}")
