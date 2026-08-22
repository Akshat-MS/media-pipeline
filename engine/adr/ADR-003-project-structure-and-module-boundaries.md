# ADR-003 · Project structure and module boundaries

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.3 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

Locked to JSON-contract stages + per-stage LXD container isolation. **v3** (during Task 4 execution): containers renamed to reflect grouping by *computational* footprint rather than by task — `pipeline-structure` / `pipeline-speech` / `pipeline-render`; confirmed no GPU on the build machine; corrected Resource Library's matching logic to run inside `pipeline-structure` (a real compute dependency on manifest+transcript data) rather than as a host-side service.

## Candidate Options

| Option | Strengths | Weaknesses |
| --- | --- | --- |
| **In-process modular monolith** `Stage` protocol, one process | Simplest to build, no container overhead | No real dependency isolation — STT/TTS's CUDA stack and Render's ffmpeg build share one environment, real conflict risk |
| **JSON-contract stages** dedicated LXD containers | True dependency isolation per stage group, independently testable by hand-feeding JSON, portable/reproducible | Upfront container build time; orchestrator must shell out via `lxc exec` |
| **Script-per-stage** no shared framework | Fastest to start writing | No shared checkpoint/error handling, no isolation — guarantees rework and dependency collisions by Day 3 |

## Recommendation & Rationale

**JSON-contract stages, grouped into three dependency-isolated LXD containers, orchestrated from the host.**

Each stage is a pure transformation: an input JSON manifest (+ referenced artifact files) in, an output JSON manifest (+ new artifact files) out. Stages never call each other's code directly — they are invoked as standalone CLI commands, e.g. `pipeline run-stage render --input <path> --output <path>`. This solves both named LXD drivers directly:

- **Dependency isolation** — the STT/TTS stack (Whisper, TTS engine, CUDA/torch) and the Render/Mux stack (a specific hardware-accelerated `ffmpeg` build) are the most conflict-prone dependency sets in this pipeline. Isolating them removes that risk entirely.
- **Portability/reproducibility** — because the interface is just JSON + files, any container image can be exported and run identically on another machine later.

**Container-to-stage grouping** (by actual dependency divergence, not one container per stage):

| Container | Stages | Why grouped this way |
| --- | --- | --- |
| `pipeline-structure` | Visual Deconstruction, Sequence Mapping, Resource Library matching | Light parsing + correlation logic — `python-pptx`, `ffprobe`, no GPU, no heavy ML. Also runs the Resource Library's matching logic (see note below) since it's a *data* dependency on manifest+transcript, not a compute dependency — no separate container needed for it. |
| `pipeline-speech` | Audio Preprocessing, Transcript Alignment | ffmpeg audio filters (`loudnorm`, denoise) + Whisper STT — grouped here because both need the speech-model environment. **No GPU passthrough** — confirmed CPU-only machine (Intel UHD integrated graphics, no NVIDIA GPU); Whisper runs on CPU, model size chosen accordingly in Task 5. *(No TTS — narration is the pre-recorded lecture track, only transcribed, never generated.)* |
| `pipeline-render` | HTML Build, Video Compose | Hardware-accelerated `ffmpeg` build for compositing — different flags/version than `pipeline-structure`'s lightweight probing use |

> **Host ↔ container interface:** one shared host directory (`res/workdir/`) bind-mounted into every container at `/workdir` (read-write, per-job). `res/library/` is bind-mounted at `/resources` — **read-write in `pipeline-structure`**, **read-only in `pipeline-render`**, and not mounted at all in `pipeline-speech` (it never touches visual assets). The orchestrator runs on the **host**, never inside a container — it is the only component that talks to the state store (SQLite) and issues `lxc exec` calls. **Config Mgmt** stays host-side (it's plain config-file reading, no environment-specific dependency, nothing to isolate). **Resource Library is different from Config Mgmt** — corrected during Task 4 discussion: its matching logic (checking whether a deconstructed icon/component already exists) is real compute over the outputs of Visual Deconstruction and Transcript Alignment, not passive storage, so it runs as stage code *inside `pipeline-structure`* — the asset files themselves are just the bind-mounted storage.

## Risks & Trade-offs

- **Interface discipline**: stages communicate only via JSON manifests and file paths under `/workdir` — never shared in-memory state, never direct imports across stage modules.
- **Base image build time** is a real, one-time cost — budget setup time for building/validating all three images (installing torch/CUDA inside a container is not instant).
- **Mount permission mismatches**: LXD's UID-mapped containers can write files with different ownership on the host — fix once via `idmap` config, not per-job.
- **No GPU available** (confirmed during Task 4 hardware check) — `pipeline-speech` runs Whisper on CPU. This is a real, ongoing constraint: transcription will be slower than GPU inference, and Task 5 should default to a smaller Whisper model (tiny/base/small) rather than large, to keep run times reasonable.
- **Don't over-isolate Ingest** — no conflicting deps; containerizing it is for consistency, not a hard need.

## Claude Code Implementation Spec

*Spec file: `project-structure.py`*
```

# Task: Scaffold JSON-contract pipeline stages orchestrated across dedicated LXD containers.


# 1. Project layout:

#    src/pipeline/

#      __init__.py

#      cli.py                     # Typer entrypoint (host-side + in-container stage CLI)

#      orchestrator.py            # Host-side runner: sequences stages, handles resume,

#                                  # invokes stages via `lxc exec`, writes checkpoints

#      stages/

#        __init__.py

#        base.py                  # Stage protocol: run(input_manifest) -> output_manifest

#        ingest.py                 # PPTX/MP4 parsing stage

#        align.py                  # Content/timing alignment (STT-driven)

#        narrate.py                 # TTS/narration generation stage

#        render.py                  # Video rendering stage

#        mux.py                       # Final audio/video muxing stage

#      state/

#        db.py, schema.sql, repository.py, migrations/

#      models/

#        schemas.py                # Pydantic models: JobConfig, StageManifest, Artifact

#      utils/

#        ffmpeg_wrapper.py, logging.py

#    infra/lxd/

#      profiles/                   # ingest.yaml, stt-narrate.yaml, render-mux.yaml

#      images/                     # per-container build scripts / dependency manifests

#      STAGE_CONTAINER_MAP.md      # documents which stage runs in which container

#    tests/

#      unit/                       # per-stage isolated tests (feed JSON by hand)

#      fixtures/                   # small sample .pptx/.mp4 files, <1MB each


# 2. Define src/pipeline/stages/base.py:
class Stage(Protocol):
    name: str
    def run(self, input_manifest: StageManifest) -> StageManifest: ...
    def validate_output(self, result: StageManifest) -> bool: ...


# Each stage's module also exposes a CLI entrypoint:

#   pipeline run-stage  --input  --output 

# — this is the ONLY way the orchestrator invokes it; no direct Python

# imports between stage modules, no in-process calls.


# 3. Define src/pipeline/models/schemas.py using Pydantic v2:

#    - JobConfig(job_id, source_path, config)

#    - StageManifest(schema_version, stage_name, artifacts: list[Artifact], metadata: dict)

#    - Artifact(artifact_type, file_path, checksum)


# 4. Orchestrator invokes stages via container exec, not function calls:
class ContainerStageRunner:
    def run_stage(self, container_name, stage_name, input_path, output_path):
        subprocess.run([
            "lxc", "exec", container_name, "--",
            "pipeline", "run-stage", stage_name,
            "--input", input_path, "--output", output_path
        ], check=True, capture_output=True)

STAGE_CONTAINER_MAP = {
    "visual_deconstruction": "pipeline-structure",
    "sequence_mapping":      "pipeline-structure",
    "audio_preprocessing":   "pipeline-speech",
    "transcript_alignment":  "pipeline-speech",
    "html_build":            "pipeline-render",
    "video_compose":         "pipeline-render",
}

# Illustrative — the real core/registry.py (Task 6) starts EMPTY on purpose.

# Module names are decided at implementation time, not guessed upfront; this

# map is populated one real entry at a time via register_stage(), only once

# each module is actually built. Config Mgmt stays host-side, never in this

# map. Resource Library's matching logic lives inside pipeline-structure's

# stage code — it's not a separate entry either.


# 5. Add a stage registry (STAGE_ORDER: list[str]) in orchestrator.py so stage

#    sequence is declared in one place, not scattered across the codebase.


# 6. NOTE — deferred to a later, separate task: the actual `lxc launch` /

#    profile / image-build scripts that create the three containers. This

#    spec only defines the CONTRACT each container-hosted stage must satisfy;

#    the scaffolding scripts to create the containers and repo folders will

#    be built next, following the same parameterized-script pattern already

#    in use, adapted to this pipeline's three containers.
```
