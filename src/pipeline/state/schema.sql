-- ============================================================================
-- schema.sql — CURRENT STATE STORE SCHEMA (reference snapshot)
--
-- This file is NOT executed by the application. It's a human-readable copy
-- of what the applied migrations produce, kept here purely so you can see
-- the full current schema in one place without reading through every
-- migration file.
--
-- The actual source of truth is src/pipeline/state/migrations/*.sql,
-- applied in order by the migration runner (src/pipeline/state/db.py) on
-- every startup. If this file and the migrations ever disagree, the
-- migrations are correct — update this file to match, never the reverse.
--
-- Last synced with: migrations/0001_init.sql
-- ============================================================================

-- ── schema_migrations ────────────────────────────────────────────────────
-- Tracks which migrations have been applied (Phase 1, item 1.5).
CREATE TABLE schema_migrations (
    version     TEXT PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ── jobs ─────────────────────────────────────────────────────────────────
-- One row per pipeline run.
CREATE TABLE jobs (
    id                  TEXT PRIMARY KEY,
    source_pptx_path    TEXT NOT NULL,
    source_video_path   TEXT NOT NULL,
    review_mode         TEXT NOT NULL
                            CHECK (review_mode IN ('auto', 'manual')),
    status              TEXT NOT NULL DEFAULT 'in_progress'
                            CHECK (status IN ('in_progress', 'completed', 'failed')),
    schema_version      TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ── job_stages ───────────────────────────────────────────────────────────
-- One row per stage, per job. review_status only carries real meaning on
-- the three gated stages; everything else stays 'not_applicable'.
CREATE TABLE job_stages (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    stage_name          TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    review_status       TEXT NOT NULL DEFAULT 'not_applicable'
                            CHECK (review_status IN (
                                'not_applicable', 'pending', 'approved', 'auto_approved'
                            )),
    container_name      TEXT,
    checkpoint_data     TEXT,
    attempt_count       INTEGER NOT NULL DEFAULT 0,
    error               TEXT,
    started_at          TEXT,
    completed_at        TEXT,

    UNIQUE (job_id, stage_name)
);

CREATE INDEX idx_job_stages_job_id ON job_stages(job_id);


-- ── artifacts ────────────────────────────────────────────────────────────
-- One row per output file a stage produced. A stage can produce more than
-- one artifact, hence a separate table rather than a column on job_stages.
CREATE TABLE artifacts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    stage_name          TEXT NOT NULL,
    artifact_type       TEXT NOT NULL,
    file_path           TEXT NOT NULL,
    checksum            TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_artifacts_job_id ON artifacts(job_id);
CREATE INDEX idx_artifacts_job_stage ON artifacts(job_id, stage_name);


-- ============================================================================
-- ENTITY RELATIONSHIP, IN PROSE
-- ============================================================================
-- jobs (1) ──< job_stages (many)   — one job has one row per pipeline stage
-- jobs (1) ──< artifacts (many)    — one job has one row per output file
-- job_stages.stage_name and artifacts.stage_name are not a formal foreign
-- key to each other (both just reference the same logical stage name) —
-- a stage's artifacts are found via (job_id, stage_name) on both tables.
-- ============================================================================
