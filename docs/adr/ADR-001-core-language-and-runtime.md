# ADR-001 · Core language and runtime

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.1 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

## Candidate Options

| Option | Strengths | Weaknesses |
| --- | --- | --- |
| **Python 3.12** single-language | Best-in-class media/ML ecosystem (moviepy, ffmpeg-python, whisper, pptx libs, torch/onnx), fast solo iteration, huge stdlib for local process orchestration | GIL limits true CPU parallelism (mitigated by multiprocessing for render/STT stages) |
| **Node.js/TypeScript** single-language | Excellent async I/O, strong typing with TS | Media/ML ecosystem is thin — constant shelling out to Python tools anyway, defeats "single language" goal |
| **Python + Rust/Go** dual-language | Best raw performance for render/muxing stages | Adds build toolchain complexity, FFI friction — actively hostile to a 5-day solo timeline |

## Recommendation & Rationale

**Python 3.12, single-language, with `asyncio` for I/O orchestration and `multiprocessing`/`concurrent.futures` for CPU-bound stages (STT, rendering).**

This is the only option where every pipeline stage (PPTX parsing, audio/video muxing via `ffmpeg`, STT via `whisper`/`faster-whisper`, TTS, alignment) has a mature, first-party or near-first-party library — meaning zero time spent building glue code or subprocess bridges to a second language. Async I/O covers orchestration (file watching, subprocess supervision, job queue polling); process pools cover CPU-bound stages without fighting the GIL. For a 5-day solo build, ecosystem maturity beats raw performance every time — you are not building a render farm, you're building a correct, resumable pipeline on one machine.

## Risks & Trade-offs

- **GIL bottlenecks on CPU-heavy stages** (STT, video encode) → mitigate by shelling out to `ffmpeg`/`whisper.cpp` binaries (already release the GIL) rather than pure-Python encode loops.
- **Dependency sprawl** (torch, ffmpeg bindings, pptx parsers) → pin versions aggressively on Day 1; don't let `pip install` drift mid-build.
- **Packaging/venv discipline** matters more solo than on a team — no one else will catch a broken lockfile.

## Claude Code Implementation Spec

*Spec file: `language-runtime.txt`*
```
Task: Initialize Python 3.12 project foundation for local media pipeline.

1. Create project root with `uv` (preferred) or `poetry` for dependency management.
2. Generate pyproject.toml with:
   - python = "^3.12"
   - core deps: ffmpeg-python, python-pptx, faster-whisper, pydantic>=2, 
     typer (CLI), rich (logging/progress), sqlite-utils
   - dev deps: pytest, pytest-cov, ruff, mypy
3. Enforce strict typing: mypy strict = true in pyproject.toml.
4. Create `.python-version` pinned to 3.12.x.
5. Verify `ffmpeg` binary is on PATH via a startup healthcheck script 
   (scripts/check_env.py) — fail fast with a clear error if missing.
6. Output: a runnable `python -m pipeline --help` stub via Typer CLI 
   entrypoint at src/pipeline/cli.py.
```
