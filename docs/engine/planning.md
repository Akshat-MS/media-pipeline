# Planning

Project-level status tracker. For the detailed 6-phase task/tech/risk
breakdown, see `media-automation-platform-blueprint.html` (interactive,
status-trackable within Claude). For Phase 1's full design rationale and
diagrams, see `1-lecture-alive-ai-foundation.html`.

---

## Phase 1 — Pipeline Foundations & Project Setup

**Status: ✅ Complete** — tagged `phase1-complete` on GitHub.

| Deliverable | Location |
|---|---|
| Repo & folder structure | `bootstrap/01_setup_repo.py` |
| State store (SQLite, WAL) | `src/pipeline/state/` |
| 3 LXD containers (`pipeline-structure`, `pipeline-speech`, `pipeline-render`) | `infra/lxd/`, `bootstrap/02_create_containers.sh` |
| Stage contract (`Stage` protocol, manifests, registry) | `src/pipeline/core/` |
| Orchestrator (fork/join, resumability, retry, review gating) | `src/pipeline/orchestrator.py` |
| Schema versioning (envelope + migrations) | `src/pipeline/models/` |
| Quality validation (8 gates, gate/advisory split) | `src/pipeline/validation/` |
| Test suite | `tests/` — 78 tests, ~96% coverage |

**Notable decisions made during execution** (see the ADR's Execution Sequence
section for full detail):
- No TTS anywhere — narration is the pre-recorded lecture audio, only
  transcribed, never generated.
- Containers grouped by *computational* footprint, not by pipeline task.
- Confirmed CPU-only dev machine — no GPU passthrough; Whisper (Phase 3)
  will run on CPU.
- Resource Library's matching logic runs inside `pipeline-structure` (a
  compute dependency on manifest+transcript data), not as a host-side
  service.
- Python constraint relaxed to `<3.14` (dev machine runs 3.13; no
  3.12-only features used anywhere).

`src/pipeline/modules/` is intentionally empty — module names and
boundaries are decided at implementation time, not guessed in Phase 1.

---

## Phase 2 — Visual Deconstruction Engine

**Status: ⬅ Next up.**

Per the blueprint (steps 2.1–2.5):

| Step | Task |
|---|---|
| 2.1 | Finalize PPTX parsing engine and MP4/video parsing engine |
| 2.2 | Finalize approach for visual tree extraction (DOM-like structure) |
| 2.3 | Build input processing pipeline: ingest PPTX/MP4 → normalize into internal visual tree |
| 2.4 | Design asset isolation logic (images, text blocks, embedded media) |
| 2.5 | Design and generate `manifest.json` schema |

This is the first real module built inside `src/pipeline/modules/`, running
in the `pipeline-structure` container (see `infra/lxd/profiles/structure.yaml`).
Dependencies (`python-pptx`, `ffprobe`, etc.) get installed into that
container only once implementation actually needs them — not pre-installed
speculatively, per the Phase 1 "shape now, contents later" pattern.

---

## Phases 3–6 — Not Yet Started

See `media-automation-platform-blueprint.html` for the full breakdown:

- **Phase 3** — Audio/Transcript Synchronization & Alignment
- **Phase 4** — Sequence Mapping, Asset Library & Execution Strategy
- **Phase 5** — Rendering & Composition Engine
- **Phase 6** — Human-in-the-Loop Review Gates & Production Scaling
