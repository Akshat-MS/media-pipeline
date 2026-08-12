"""
SQLite connection setup + migration runner for the pipeline state store.

This is the ONLY file that opens a raw sqlite3.Connection. Everything else
(including repository.py) receives an already-configured connection —
nothing else should call sqlite3.connect() directly.

Per Phase 1, item 1.2: single SQLite file, WAL mode, host-side only.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────

# repo_root/src/pipeline/state/db.py -> repo_root is 3 parents up
_REPO_ROOT = Path(__file__).resolve().parents[3]
_MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

DEFAULT_DB_PATH = _REPO_ROOT / ".pipeline" / "state.db"


def default_db_path() -> Path:
    """
    Resolve the state DB path. Honors PIPELINE_DB_PATH env var (used by
    tests to point at a throwaway file) — falls back to .pipeline/state.db
    at the repo root otherwise.
    """
    override = os.environ.get("PIPELINE_DB_PATH")
    return Path(override) if override else DEFAULT_DB_PATH


# ── Migration runner ─────────────────────────────────────────────────────

def _applied_migrations(conn: sqlite3.Connection) -> set[str]:
    """
    Return the set of migration versions already applied. The very first
    migration creates the schema_migrations table itself, so on a brand
    new database this table won't exist yet — that's expected, not an
    error, and just means "nothing applied so far."
    """
    try:
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
        return {row[0] for row in rows}
    except sqlite3.OperationalError:
        return set()


def apply_migrations(conn: sqlite3.Connection, migrations_dir: Path = _MIGRATIONS_DIR) -> list[str]:
    """
    Apply any migration files under migrations_dir that haven't already
    been recorded in schema_migrations, in filename order (0001_, 0002_, ...).
    Each migration file is expected to record its own version via
    INSERT INTO schema_migrations (per Phase 1, item 1.5).

    Returns the list of versions applied during this call (empty if the
    database was already up to date).
    """
    applied = _applied_migrations(conn)
    migration_files = sorted(migrations_dir.glob("*.sql"))

    newly_applied: list[str] = []
    for path in migration_files:
        version = path.stem  # e.g. "0001_init"
        if version in applied:
            continue
        sql = path.read_text()
        conn.executescript(sql)
        newly_applied.append(version)

    return newly_applied


# ── Connection factory ───────────────────────────────────────────────────

def connect(db_path: Path | None = None, *, run_migrations: bool = True) -> sqlite3.Connection:
    """
    Open a connection to the state store with WAL mode + foreign keys
    enabled, applying any pending migrations first. This is the single
    entrypoint every other module should use to get a connection.
    """
    path = db_path if db_path is not None else default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")

    if run_migrations:
        apply_migrations(conn)

    return conn
