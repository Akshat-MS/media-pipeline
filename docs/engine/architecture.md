# Pipeline Architecture

**Phase 1 — Foundations.** Status: complete (tag `phase1-complete`).

> Converted from `architecture.html` during the docs restructure. The seven
> numbered Phase 1 decisions have been extracted: six into `docs/adr/` as
> append-only decision records, and section 1.6 into
> `docs/shared/requirements/quality-thresholds.md`. This document keeps the
> architecture, the diagrams, and an index pointing at them.

Local-First Media Automation Pipeline (PPTX/MP4 → Aligned, Narrated, Rendered Video)

## System Architecture

Major building blocks and how they interact — grouped by role, not execution order.

![Fig. 1 — System architecture. Audio Preprocessing cleans the recorded track once and feeds both Transcript Alignment and the final Video Compose. Manifest & Plan reviews run inline; Plan Review is the human-edit point. Config Mgmt feeds Rendering directly and is read-only.](diagrams/fig-1-system-architecture.svg)

*Fig. 1 — System architecture. Audio Preprocessing cleans the recorded track once and feeds both Transcript Alignment and the final Video Compose. Manifest & Plan reviews run inline; Plan Review is the human-edit point. Config Mgmt feeds Rendering directly and is read-only.*

## Pipeline Execution & Data Flow

Task-by-task execution flow, with data-artifact and review connections shown explicitly.

![Fig. 2 — Pipeline execution & data flow. Top-to-bottom task order: parallel Visual Extraction / Audio Preprocessing → Manifest Review gate → Sequence Mapping + Resource Library → Plan Review (human edit point) → Rendering & Composition → Final Review & Sync QC → Delivery. Amber marks input and review gates; teal marks hand-offs between processing units; green marks the final output.](diagrams/fig-2-pipeline-data-flow.svg)

*Fig. 2 — Pipeline execution & data flow. Top-to-bottom task order: parallel Visual Extraction / Audio Preprocessing → Manifest Review gate → Sequence Mapping + Resource Library → Plan Review (human edit point) → Rendering & Composition → Final Review & Sync QC → Delivery. Amber marks input and review gates; teal marks hand-offs between processing units; green marks the final output.*

**Legend:** Input / Review Gate · Processing hand-off · Resource Library (read+write) · Final output

### 1.1 · Core Language & Runtime Finalization

→ [ADR-001 · Core language and runtime](../adr/ADR-001-core-language-and-runtime.md)
### 1.2 · Local State Store Finalization

→ [ADR-002 · Local state store](../adr/ADR-002-local-state-store.md)
### 1.3 · Project Structure & Module Boundaries

→ [ADR-003 · Project structure and module boundaries](../adr/ADR-003-project-structure-and-module-boundaries.md)
### 1.4 · Job Resumability & Checkpointing

→ [ADR-004 · Job resumability and checkpointing](../adr/ADR-004-job-resumability-and-checkpointing.md)
### 1.5 · Schema Versioning Strategy

→ [ADR-005 · Schema versioning strategy](../adr/ADR-005-schema-versioning-strategy.md)
### 1.6 · Quality & Validation Thresholds

→ [Quality & Validation Thresholds](../shared/requirements/quality-thresholds.md)
### 1.7 · Testing & Local CI Infrastructure

→ [ADR-006 · Testing and local CI](../adr/ADR-006-testing-and-local-ci.md)

---

## Phase 1 Execution Sequence

The seven design decisions above are finalized; this is the build order for turning them into a working local foundation, and the order in which the GitHub repo will reflect progress.

1. **Repo & folder structure scaffold ✓ DONE**
`src/pipeline/...` · `infra/lxd/...` · `tests/...` · `.github/` — **Depends on:** — · **Relates to:** 1.3
Built via `bootstrap/01_setup_repo.py` — idempotent, tested with `--dry-run` before real execution.
2. **Git init + first commit + push to GitHub ✓ DONE**
**Depends on:** Step 1
Pushed to `github.com/Akshat-MS/media-pipeline` over SSH (switched from HTTPS after GitHub rejected password auth).
3. **State store schema ✓ DONE**
`state/schema.sql`, `db.py`, `repository.py`, migration 0001 — pure host-side, no containers needed — **Depends on:** Step 1 · **Relates to:** 1.2
**Learned during build:** added `review_mode` (on `jobs`) and `review_status` (on `job_stages`) columns, not in the original 1.2 spec — needed to support choosing `auto` vs `manual` review per job at submission time. Full lifecycle tested end-to-end against real SQLite, including checksum-based edit detection and retry/attempt-count tracking.
4. **Create the 3 LXD containers ✓ DONE**
`pipeline-structure`, `pipeline-speech`, `pipeline-render` + bind-mount `/workdir` & `/resources` — **Depends on:** Step 1 · **Relates to:** 1.3
**Learned during build:** containers named/grouped by *computational* footprint, not by pipeline task — confirmed CPU-only machine (no NVIDIA GPU), so no GPU passthrough anywhere. Resource limits sized to the real machine: `pipeline-structure` 2 CPU/2GB, `pipeline-speech` 3 CPU/4GB (heaviest — Whisper CPU inference), `pipeline-render` 2 CPU/2GB, 8GB disk each. Hit and fixed a real bug: the host's `default` LXD profile has no network device, so each profile now defines its own `eth0` explicitly rather than relying on `--profile default`. Added an explicit per-container internet-connectivity check (using bash's `/dev/tcp`, not `curl` — a bare image doesn't have `curl` yet) before attempting `apt-get`, so a network problem fails fast with a clear message.
5. **Install per-container dependencies ↻ DEFERRED — INCREMENTAL**
ffprobe/python-pptx; whisper (CPU); hw-accel ffmpeg — **Depends on:** Step 4 · **Relates to:** 1.3
**Decision made during build:** rather than installing every module's dependencies upfront, each container only gets baseline tooling now (`python3`, `pip`, `build-essential`, `curl`) — real module-specific packages are installed one at a time, only once we're actually implementing the module that needs them. This avoids guessing at a dependency list before real module boundaries are proven.
6. **Stage contract skeleton ✓ DONE**
`core/stage_protocol.py`, `core/manifest.py`, `core/registry.py`, `models/schemas.py` — **Depends on:** Steps 1, 4 · **Relates to:** 1.3
**Learned during build:** resolved an overlap from the original folder-structure sketch — `StageManifest`/`Artifact` live in `core/manifest.py` (tightly bound to the `Stage` protocol), `models/schemas.py` narrowed to just `JobConfig`. `core/registry.py` is intentionally empty (`STAGE_ORDER`, `STAGE_CONTAINER_MAP` both start as `{}`/`[]`) — real stage names are registered one at a time via `register_stage()` as modules are actually built, never guessed upfront. Verified the `Stage` Protocol's structural typing works correctly (a plain class satisfies it with zero inheritance) and that pydantic validation correctly rejects malformed input.
7. **Orchestrator skeleton ☐ NEXT**
`orchestrator.py`, `ContainerStageRunner`, checkpoint/resume logic — **Depends on:** Steps 3, 6 · **Relates to:** 1.3, 1.4
**Known going in:** the dependency graph is not strictly linear — Sequence Mapping and Resource Library matching both need *both* Visual Deconstruction's and Transcript Alignment's output (a fork/join), not a single chain. The orchestrator must express that, not just iterate a flat `STAGE_ORDER` list.
8. **Schema versioning envelope + migration framework ☐ PENDING**
`models/envelope.py`, `migrations.py` — **Depends on:** Step 6 · **Relates to:** 1.5
9. **Validation/threshold framework ☐ PENDING**
`validation/thresholds.py`, `validators.py` — **Depends on:** Steps 6, 7 · **Relates to:** 1.6
10. **Test scaffold + fixtures + Makefile/justfile ☐ PENDING**
**Depends on:** Steps 6, 7, 8, 9 · **Relates to:** 1.7
11. **Commit + push full Phase 1 foundation to GitHub ☐ PENDING**
**Depends on:** all above

> **Note on GitHub sync**: steps 2 and 11 bookend the day — the empty skeleton is pushed first so every subsequent step is a reviewable diff, and the final push closes out Phase 1 with a complete, working foundation in the remote. In practice, commits are happening after each completed step (1, 3, 4, 6 so far) rather than being batched — smaller, reviewable diffs tied to one task each.

---

## Phase 1 Summary Table — Final

| Item | Decision | Design Status | Completed |
| --- | --- | --- | --- |
| **1.1** Language/Runtime | Python 3.12, asyncio + multiprocessing | **FINAL** | **DONE** — pyproject.toml scaffolded (Step 1) |
| **1.2** State Store | SQLite (WAL mode), repository pattern, host-side only | **FINAL** | **DONE** — schema, db.py, repository.py built & tested (Step 3) |
| **1.3** Architecture | JSON-contract stages, 3 dependency-isolated LXD containers, host-side orchestrator | **↻ REVISED v3** | **↻ IN PROGRESS** — containers live (Step 4), stage contract built (Step 6); orchestrator + real modules still pending (Step 7+) |
| **1.4** Resumability | Per-stage checkpointing = per-container-invocation checkpointing | **FINAL** | **↻ PARTIAL** — state-store support built & tested (checksum-based edit detection, retry tracking); orchestrator logic not yet built (Step 7) |
| **1.5** Schema Versioning | Strict semver, envelope, read-time migrations | **FINAL** | **NOT STARTED** — Step 8 |
| **1.6** Quality Thresholds | Fixed 24-30fps + full delivered-output spec · 80ms sync drift · 12% WER (advisory) · integrity checks | **↻ REVISED v2** | **DONE** — Step 9, 87 passing tests |
| **1.7** Testing/CI | pytest + golden files + property tests, no external CI | **FINAL** | **NOT STARTED** — Step 10 |

**Legend:** *Design Status* = whether the decision/spec itself is locked (all seven are Final as of this document). *Completed* = whether it has actually been built/implemented yet (containers created, code scaffolded, pushed to GitHub) — update this column as execution sequence steps 1–11 are completed, so this table stays the single source of truth for both "what we decided" and "what's actually done."

**Deferred to next working session:** actual LXD container creation scripts (3 containers, named per the map in 1.3), workspace/repo folder scaffolding, and the concrete CI/quality-check tooling install — all to be built next, following the parameterized-script pattern already in your toolkit rather than from scratch.

All seven decisions are locked to the single constraint governing this build: maximum solo velocity on one machine within 5 days, deferring every distributed/multi-tenant/heavy-infra concern to a hypothetical future phase this build does not need to anticipate today.

---

## Phase 2 — Config Mgmt

**Status:** design finalized. Implementation not yet started.

Eight design questions from `docs/engine/config-mgmt-handoff.md` § 3, all
decided together in a single combined ADR rather than one per question.

→ [ADR-007 · Config Mgmt (all eight design questions)](../adr/ADR-007-config-mgmt.md)

![Fig. 3 — Config Mgmt internal pipeline. The committed style contract JSON flows through parse, validate, version, and resolve inside services/config/, producing a single resolved, immutable config object consumed by Rendering. A future config-authoring UI is out of scope.](diagrams/fig-3-config-mgmt-pipeline.svg)

*Fig. 3 — Config Mgmt internal pipeline, zoomed in from Fig. 1's single "Config Mgmt" box. Each internal stage is tagged with the design question that shapes it.*

### Phase 2 Summary Table

| Item | Decision | Design Status | Completed |
| --- | --- | --- | --- |
| **2.1** Placement & module layout | `src/pipeline/services/config/`, flat: `loader.py` / `models.py` / `resolver.py` | **FINAL** | **NOT STARTED** |
| **2.2** Theme resolution | Resolve once at load → flat token set; default `navy`; unknown theme name still fails loudly | **FINAL** | **NOT STARTED** |
| **2.3** Validation model | All fields mandatory except `theme_selected` / `slide_transition.type` / declared fallbacks; fail loudly with field path | **FINAL** | **NOT STARTED** |
| **2.4** Schema versioning | Contract-specific envelope (not `SchemaEnvelope`); no migration registered yet at `1.0.0` | **FINAL** | **NOT STARTED** |
| **2.5** Encode-target ownership | `delivery-targets.md` remains owner; drift caught by a cross-check test, not runtime coupling | **FINAL** | **NOT STARTED** |
| **2.6** Immutability & access | Plain `load_style_contract()` function, called once, passed explicitly — no singleton | **FINAL** | **NOT STARTED** |
| **2.7** Override precedence | CLI arg → `PIPELINE_STYLE_THEME` env var → contract's `theme_selected` → navy floor; winning source logged | **FINAL** | **NOT STARTED** |
| **2.8** Forward fit for Layer 4 | Loader stays style-contract-specific; revisit generalization once Layer 4 has a real schema | **FINAL** | **NOT STARTED** |

**Legend:** same convention as the Phase 1 table above — *Design Status* is
whether the decision is locked; *Completed* tracks actual implementation
and updates as build steps land.
