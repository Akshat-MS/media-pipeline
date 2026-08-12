-- ============================================================================
-- Migration 0001 — init
-- Creates the three core state-store tables: jobs, job_stages, artifacts.
-- Also creates the schema_migrations tracking table itself (bootstrap).
--
-- This file is the SOURCE OF TRUTH — it's what the migration runner actually
-- executes. src/pipeline/state/schema.sql is a human-readable snapshot of
-- the resulting schema, kept in sync for reference; it is never executed
-- directly.
-- ============================================================================

BEGIN;

-- ── Migration tracking ──────────────────────────────────────────────────
-- Records which migrations have been applied, so re-running setup never
-- tries to recreate existing tables (per Phase 1, item 1.5).
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,          -- e.g. '0001_init'
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ── jobs ─────────────────────────────────────────────────────────────────
-- One row per pipeline run. review_mode is chosen once, at job submission,
-- and does not change mid-run (Phase 1, item 3 discussion — auto vs manual
-- review).
CREATE TABLE jobs (
    id                  TEXT PRIMARY KEY,          -- e.g. 'job_20260812_ab12'
    source_pptx_path    TEXT NOT NULL,
    source_video_path   TEXT NOT NULL,
    review_mode         TEXT NOT NULL
                            CHECK (review_mode IN ('auto', 'manual')),
    status              TEXT NOT NULL DEFAULT 'in_progress'
                            CHECK (status IN ('in_progress', 'completed', 'failed')),
    schema_version      TEXT NOT NULL,             -- semver, per item 1.5
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ── job_stages ───────────────────────────────────────────────────────────
-- One row per stage, per job (latest attempt's state — attempt_count
-- increments in place rather than inserting a new row per retry).
--
-- review_status only carries meaning on the three gated stages (whichever
-- stage precedes Manifest Review, Sequence Mapping before Plan Review,
-- Video Compose before Final Review). Non-gated stages stay
-- 'not_applicable'. In auto review_mode, gated stages resolve straight to
-- 'auto_approved' rather than pausing on 'pending' — this preserves an
-- audit trail of which gates a job passed through and how, distinct from
-- stages that were never gated at all.
CREATE TABLE job_stages (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    stage_name          TEXT NOT NULL,              -- e.g. 'visual_extraction'
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    review_status       TEXT NOT NULL DEFAULT 'not_applicable'
                            CHECK (review_status IN (
                                'not_applicable', 'pending', 'approved', 'auto_approved'
                            )),
    container_name      TEXT,                       -- which container ran this (nullable
                                                      -- until first execution — filled at
                                                      -- runtime, per item 1.3)
    checkpoint_data     TEXT,                        -- JSON: input checksums, output
                                                      -- artifact refs, duration, etc.
    attempt_count       INTEGER NOT NULL DEFAULT 0,
    error               TEXT,
    started_at          TEXT,
    completed_at        TEXT,

    UNIQUE (job_id, stage_name)
);

CREATE INDEX idx_job_stages_job_id ON job_stages(job_id);


-- ── artifacts ────────────────────────────────────────────────────────────
-- One row per output file a stage produced. checksum is what lets the
-- orchestrator detect a human-edited file (e.g. plan.json changed after
-- Sequence Mapping ran) and invalidate the correct downstream checkpoints
-- (per item 1.4 resumability).
--
-- A single stage can produce more than one artifact (e.g. Sequence Mapping
-- emits both plan.json and a plain-text version) — that's why this is a
-- separate table from job_stages rather than a column on it.
CREATE TABLE artifacts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    stage_name          TEXT NOT NULL,              -- which stage produced this
    artifact_type       TEXT NOT NULL,              -- e.g. 'manifest', 'plan_json',
                                                      -- 'plan_text', 'final_video'
    file_path           TEXT NOT NULL,               -- path under res/workdir/<job_id>/
                                                       -- or res/outputs/<job_id>/
    checksum            TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))  -- bumped when checksum
                                                                   -- changes (human edit)
);

CREATE INDEX idx_artifacts_job_id ON artifacts(job_id);
CREATE INDEX idx_artifacts_job_stage ON artifacts(job_id, stage_name);


-- ── Record this migration as applied ────────────────────────────────────
INSERT INTO schema_migrations (version) VALUES ('0001_init');

COMMIT;
