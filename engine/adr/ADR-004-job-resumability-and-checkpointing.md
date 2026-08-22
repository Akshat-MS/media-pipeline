# ADR-004 · Job resumability and checkpointing

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.4 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

Confirmed applicable — clarified for the container-based architecture (1.3 v2).

> **Clarification:** with stages now running as isolated LXD container invocations rather than in-process function calls, the checkpoint boundary and the container-invocation boundary become the **same boundary** — this makes resumability cleaner, not less applicable. Each `lxc exec … pipeline run-stage …` call either fully succeeds or fails outright; there is no in-process partial state to worry about, since every stage starts fresh from its input JSON manifest every time.

## Concrete Design

**Checkpoint granularity = per-stage (= per-container-invocation), not per-substep.** Each of the five stages (Ingest, Align, Narrate, Render, Mux) is the atomic unit of resumability. A stage either completes fully or is retried from scratch — no partial-stage resume. This is the correct granularity for a 5-day build: per-substep checkpointing adds real engineering cost for a benefit you won't hit often at local, single-job scale.

**Checkpoint contents** (persisted to `job_stages.checkpoint_data` as JSON):

checkpoint\_data · example.json

```
{
  "stage_name": "render",
  "status": "completed",
  "input_checksums": {"aligned_script.json": "sha256:...", "narration.wav": "sha256:..."},
  "output_artifacts": [
    {"type": "video/mp4", "path": "workdir/render/output.mp4", "checksum": "sha256:..."}
  ],
  "attempt_count": 1,
  "duration_seconds": 143.2
}
```

## Resume Logic

1. On job start, orchestrator queries `get_resumable_jobs()` for status = `in_progress` or `failed`.
2. For each stage in order, check `job_stages.status`. If `completed` **and** input checksums still match current inputs → skip (no container invocation needed). If checksums mismatch → invalidate downstream checkpoints and re-run from that stage forward via its container.
3. If `failed` → retry via a fresh `lxc exec` invocation (bounded by `attempt_count`, max 3 before surfacing to user). The container itself needs no awareness of retry state — that logic lives entirely in the host-side orchestrator.

## Trade-offs & Edge Cases

- **Stale checkpoints on changed inputs**: always validate via checksum, never trust a "completed" status blindly.
- **Partial file writes on crash**: stages must write outputs to a temp path and atomically rename on success (`os.replace`).
- **Non-deterministic stages** (TTS voice variance): checkpointing by checksum still works since you're checkpointing output artifacts, not re-deriving determinism.

## Claude Code Implementation Spec

*Spec file: `resumability.txt`*
```
Task: Implement checkpoint/resume logic in the orchestrator.

1. Add src/pipeline/orchestrator.py logic:
   - compute_checksum(path) -> sha256 hex digest (streamed, chunked read)
   - should_skip_stage(stage, ctx) -> bool: compares job_stages checkpoint
     input_checksums against current input artifact checksums
   - run_stage_with_checkpoint(stage, ctx): wraps ContainerStageRunner.run_stage()
     (from 1.3) in try/except, expects output written to //.tmp/
     inside the container, atomic-renames on success (host-side, since /workdir
     is bind-mounted), persists checkpoint_data via repository.save_checkpoint()
     including which container_name executed the stage
2. Add retry policy: max_attempts=3 per stage, exponential backoff
   (2s, 8s, 32s) between retries, configurable via pipeline.toml.
3. Add CLI command `pipeline resume ` that re-invokes orchestrator
   with resume=True, skipping validated-complete stages.
4. Add CLI command `pipeline status ` showing per-stage status,
   checksums, and last error (if any) as a Rich table.
5. Unit tests: simulate a crash mid-stage (raise exception in stage 3 of 5),
   assert resume skips stages 1-2 and retries stage 3 only.
```
