# media-pipeline

Local-first media automation pipeline: PPTX + lecture video (MP4) in,
aligned / synced rendered video out.

See `docs/1-media-pipeline-foundation.html` for the full Phase 1 architecture,
design decisions, and diagrams.

## Quick start

```bash
python3 bootstrap/01_setup_repo.py     # you're running this now
# next: bootstrap/02_create_containers.sh, etc. — see bootstrap/README.md
```

## Layout

- `src/pipeline/` — application code (modules, services, state, orchestrator)
- `infra/` — declarative LXD container config (profiles, provisioning)
- `bootstrap/` — one-time setup scripts
- `res/` — inputs / outputs / workdir / resource library
- `tests/` — unit, integration, golden-file, fixtures
- `docs/` — architecture, ADRs, diagrams, reference docs
