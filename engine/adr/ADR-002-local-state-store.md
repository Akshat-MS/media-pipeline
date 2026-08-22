# ADR-002 · Local state store

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.2 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

## Candidate Options

| Option | Strengths | Weaknesses |
| --- | --- | --- |
| **SQLite** file-based, WAL mode | Zero-ops, ACID, handles concurrent readers + single writer cleanly, native Python support, trivially inspectable | Not built for high write concurrency (irrelevant here — single pipeline process) |
| **Flat JSON/YAML files** per job | Dead simple, human-readable, git-diffable | No transactional guarantees — a crash mid-write corrupts state; no query capability across jobs |
| **Postgres** local daemon | Full RDBMS features, familiar tooling | Requires a running service, backup/restore ceremony, connection pooling — pure overkill for one machine |

## Recommendation & Rationale

**SQLite in WAL mode, single file at `.pipeline/state.db`, accessed through a thin repository layer.**

SQLite gives you crash-safe, transactional writes (critical for checkpointing — see 1.4) with zero operational overhead: no daemon to start, no port to manage, no backup strategy beyond copying a file. WAL mode specifically solves the "concurrency" risk — it allows the main process to write job state while a monitoring/CLI-status process reads concurrently, without lock contention. This is the correct middle point between "flat files" (durability risk) and "Postgres" (infrastructure you don't need).

## Risks & Trade-offs

- **Schema migrations are manual** — no SQLite migration framework is bundled; must hand-roll a lightweight migration runner or the schema will drift silently.
- **Large blob storage** (rendered frames, audio buffers) should **never** go into SQLite rows — store as files on disk, reference by path in the DB.
- **Single-writer constraint**: if you later parallelize multiple pipeline jobs, writes must be serialized through one connection/queue — fine at solo scale.

## Claude Code Implementation Spec

*Spec file: `state-store.txt`*
```
Task: Set up SQLite-backed local state store with WAL mode and repository pattern.

1. Create src/pipeline/state/db.py:
   - Initialize SQLite connection at .pipeline/state.db
   - PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; on every connection open
2. Create src/pipeline/state/schema.sql with initial tables:
   - jobs (id TEXT PK, source_path TEXT, status TEXT, schema_version TEXT,
     created_at, updated_at)
   - job_stages (id INTEGER PK, job_id FK, stage_name TEXT, status TEXT,
     checkpoint_data TEXT (JSON), started_at, completed_at, error TEXT)
   - artifacts (id INTEGER PK, job_id FK, stage_name TEXT, artifact_type TEXT,
     file_path TEXT, checksum TEXT, created_at)
3. Create src/pipeline/state/migrations/ with a numbered migration runner
   (0001_init.sql, 0002_*.sql...) applied on startup via a simple
   "schema_migrations" tracking table.
4. Create src/pipeline/state/repository.py exposing typed methods:
   create_job(), update_stage_status(), get_resumable_jobs(),
   save_checkpoint(), get_last_checkpoint() — no raw SQL outside this file.
5. Add a CLI command `pipeline db inspect` (Typer) that dumps current job/stage
   status as a Rich table for quick local debugging.
```
