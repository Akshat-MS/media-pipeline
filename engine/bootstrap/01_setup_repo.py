#!/usr/bin/env python3
# ==============================================================================
# ▶  WHERE TO RUN : YOUR LOCAL MACHINE (laptop / desktop)
# ▶  WHEN         : Once — Phase 1, Task 1 — before anything else
# ▶  PURPOSE      : Create the full media-pipeline folder structure + starter
#                   config files (pyproject.toml, .gitignore, justfile, etc.)
# ▶  HOW          : python3 01_setup_repo.py
#                   python3 01_setup_repo.py --dry-run        (preview only)
#                   python3 01_setup_repo.py --repo-root /path/to/media-pipeline
#
# ▶  NOTE         : This script creates STRUCTURE only — empty module/service
#                   folders under src/pipeline/modules/ are intentionally left
#                   unnamed (per Phase 1 decision: module names are decided at
#                   implementation time, not during scaffolding). Likewise,
#                   tests/, res/ subfolders are created empty with .gitkeep —
#                   no placeholder module or fixture files are invented here.
# ==============================================================================

import argparse
import sys
from pathlib import Path

# ── Colour helpers for terminal output ────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

def ok(msg):     print(f"{GREEN}  ✓  {msg}{RESET}")
def info(msg):   print(f"{CYAN}  →  {msg}{RESET}")
def warn(msg):   print(f"{YELLOW}  !  {msg}{RESET}")
def error(msg):  print(f"{RED}  ✗  {msg}{RESET}", file=sys.stderr)
def header(msg): print(f"\n{CYAN}{'─'*64}\n  {msg}\n{'─'*64}{RESET}")


# ── Folder structure ───────────────────────────────────────────────────────
# Matches the Phase 1 ADR (docs/1-media-pipeline-foundation.html), section 1.3
# and the folder-structure discussion that followed it.
DIRS = [
    # --- src/pipeline ---
    "src/pipeline/core",
    "src/pipeline/modules",                     # left empty — names TBD at implementation
    "src/pipeline/services/resource_library",
    "src/pipeline/services/config",
    "src/pipeline/state/migrations",
    "src/pipeline/models",
    "src/pipeline/validation",
    "src/pipeline/utils",

    # --- tests ---
    "tests/unit/modules",
    "tests/integration",
    "tests/golden",
    "tests/fixtures",

    # --- res (data — inputs/outputs/workdir are runtime-populated per job) ---
    "res/inputs",
    "res/outputs",
    "res/workdir",
    "res/library/icons",
    "res/library/components",
    "res/library/templates",

    # --- infra (declarative container config — no container names yet) ---
    "infra/lxd/profiles",
    "infra/lxd/provisioning",

    # --- bootstrap (this script lives here too) ---
    "bootstrap",

    # --- docs (flat, no nesting — per Phase 1 decision) ---
    "docs",

    # --- CI placeholder, empty per 1.7 (no external CI for Phase 1) ---
    ".github/workflows",
]

# Directories that are Python packages and need an __init__.py
PACKAGES = [
    "src/pipeline",
    "src/pipeline/core",
    "src/pipeline/modules",
    "src/pipeline/services",
    "src/pipeline/services/resource_library",
    "src/pipeline/services/config",
    "src/pipeline/state",
    "src/pipeline/models",
    "src/pipeline/validation",
    "src/pipeline/utils",
]

# Directories that are otherwise empty and need a .gitkeep so git tracks them
GITKEEP_DIRS = [
    "tests/unit/modules",
    "tests/integration",
    "tests/golden",
    "tests/fixtures",
    "res/inputs",
    "res/outputs",
    "res/workdir",
    "res/library/icons",
    "res/library/components",
    "res/library/templates",
    "infra/lxd/profiles",
    "infra/lxd/provisioning",
    ".github/workflows",
    "src/pipeline/state/migrations",
]


# ── File contents ─────────────────────────────────────────────────────────

PYPROJECT_TOML = """\
[project]
name = "media-pipeline"
version = "0.1.0"
description = "Local-first media automation pipeline (PPTX/MP4 -> aligned, synced video)"
requires-python = ">=3.12,<3.13"

dependencies = [
    "ffmpeg-python>=0.2",
    "python-pptx>=1.0",
    "faster-whisper>=1.0",
    "pydantic>=2.6",
    "typer>=0.12",
    "rich>=13.7",
    "sqlite-utils>=3.36",
    "jiwer>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.9",
]

[project.scripts]
pipeline = "pipeline.cli:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["unit", "integration", "slow"]

[tool.mypy]
strict = true

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pipeline"]
"""

GITIGNORE = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.env
.env.*

# Build / dist
dist/
build/

# Runtime state (Phase 1, item 1.2) — local, disposable, never versioned
.pipeline/

# Per-job data (Phase 1, res/ design) — folders tracked via .gitkeep,
# their generated contents are not
res/inputs/*
res/outputs/*
res/workdir/*
!res/inputs/.gitkeep
!res/outputs/.gitkeep
!res/workdir/.gitkeep

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""

PYTHON_VERSION = "3.12\n"

JUSTFILE = """\
# Run unit tests only (fast — no media I/O)
test:
    pytest tests/unit -v

# Run the full suite including integration + golden-file tests
test-full:
    pytest tests -v --cov=src/pipeline

# Lint + type-check + run tests — the entire "CI" for this project (1.7)
check:
    ruff check .
    mypy src/pipeline
    just test

# Show status of all jobs in the local state store
status:
    python -m pipeline.cli db inspect
"""

PRE_COMMIT_CONFIG = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]

  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit
        language: system
        pass_filenames: false
"""

ROOT_README = """\
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
"""

DOCS_README = """\
# docs/

- `1-media-pipeline-foundation.html` — Phase 1 ADR: foundational decisions,
  architecture, and pipeline diagrams
- `architecture.svg`, `pipeline_flow.svg` — standalone diagrams referenced above
- `stage_container_map.md` — reference: which stage runs in which container
- `glossary.md` — project-specific terms
- `installation.md` — environment / container setup
- `troubleshooting.md` — known issues and fixes
- `planning.md` — execution sequence, task tracking

Naming convention for phase documents: `{phase}-media-pipeline-{topic}.html`
"""

BOOTSTRAP_README = """\
# bootstrap/

One-time setup scripts. Run in order, once per machine:

1. `01_setup_repo.py`             — creates the folder structure (this script)
2. `02_create_containers.sh`      — creates the 3 LXD containers
3. `03_install_container_deps.sh` — installs dependencies inside each container
4. `04_verify_environment.sh`     — healthcheck: containers up, mounts working, GPU visible

Scripts 2-4 are not yet written — added when Task 1 is confirmed complete and
we move to container creation (Phase 1 execution sequence, steps 4-5).
"""

TESTS_FIXTURES_README = """\
# tests/fixtures/

Small sample media files (<1MB each) used by integration tests.
Nothing checked in yet — fixtures are added once the Ingest/Visual Extraction
stage is implemented and needs something real to run against.

Document here, per fixture, once added:
- what it is
- how it was generated / where it came from
- what property it's meant to exercise
"""

RES_LIBRARY_README = """\
# res/library/

Resource Library — reusable icon/component assets, read+write, shared across
all jobs (not per-job data). Populated at runtime by the pipeline whenever
Visual Extraction surfaces a visual element with no existing match.

Empty on Day 1. Subfolders (`icons/`, `components/`, `templates/`) are
placeholders; an index/lookup mechanism is added once the Resource Library
service is implemented (Phase 1 architecture, Support / Artifacts Layer).
"""

# ── File manifest ──────────────────────────────────────────────────────────
FILES = {
    "pyproject.toml":              PYPROJECT_TOML,
    ".gitignore":                  GITIGNORE,
    ".python-version":             PYTHON_VERSION,
    "justfile":                    JUSTFILE,
    ".pre-commit-config.yaml":     PRE_COMMIT_CONFIG,
    "README.md":                   ROOT_README,
    "docs/README.md":              DOCS_README,
    "docs/stage_container_map.md": "# Stage → Container Map\n\n_TBD — filled in when containers are created (Task 4)._\n",
    "docs/glossary.md":            "# Glossary\n\n_TBD._\n",
    "docs/installation.md":        "# Installation\n\n_TBD._\n",
    "docs/troubleshooting.md":     "# Troubleshooting\n\n_TBD._\n",
    "docs/planning.md":            "# Planning\n\n_TBD — see the Phase 1 ADR's execution sequence for now._\n",
    "bootstrap/README.md":         BOOTSTRAP_README,
    "tests/fixtures/README.md":    TESTS_FIXTURES_README,
    "res/library/README.md":       RES_LIBRARY_README,
}


# ── Main ───────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        default=".",
        help="Path to the root of the media-pipeline repo (default: current directory)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing anything",
    )
    return p.parse_args()


def create_dirs(repo_root: Path, dry_run: bool):
    header("Creating directory structure")
    for d in DIRS:
        full = repo_root / d
        if dry_run:
            info(f"[dry-run] mkdir {full}")
        else:
            full.mkdir(parents=True, exist_ok=True)
            ok(f"mkdir  {d}")


def create_packages(repo_root: Path, dry_run: bool):
    header("Creating Python package __init__.py files")
    for pkg in PACKAGES:
        init = repo_root / pkg / "__init__.py"
        if dry_run:
            info(f"[dry-run] touch {init}")
        elif not init.exists():
            init.write_text("")
            ok(f"touch  {pkg}/__init__.py")
        else:
            info(f"exists {pkg}/__init__.py  (skipped)")


def create_gitkeeps(repo_root: Path, dry_run: bool):
    header("Creating .gitkeep placeholders for empty directories")
    for d in GITKEEP_DIRS:
        keep = repo_root / d / ".gitkeep"
        if dry_run:
            info(f"[dry-run] touch {keep}")
        elif not keep.exists():
            keep.write_text("")
            ok(f"touch  {d}/.gitkeep")
        else:
            info(f"exists {d}/.gitkeep  (skipped)")


def create_files(repo_root: Path, dry_run: bool):
    header("Writing starter config + placeholder doc files")
    for rel_path, content in FILES.items():
        full = repo_root / rel_path
        if dry_run:
            info(f"[dry-run] write {full}")
            continue
        if full.exists():
            warn(f"exists  {rel_path}  (skipped — delete to regenerate)")
            continue
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        ok(f"write  {rel_path}")


def print_next_steps():
    header("Done!  Next steps")
    print(f"""
  {CYAN}1. Review what was created{RESET}
     tree -L 3 -a --gitignore   (or just browse the folders)

  {CYAN}2. Install dependencies (once you're ready to write code){RESET}
     uv sync --all-extras   # or: pip install -e ".[dev]"

  {CYAN}3. Git init + first commit + push{RESET}
     git init
     git add .
     git commit -m "chore: Phase 1 Task 1 — repo & folder structure scaffold"
     git remote add origin <your-repo-url>
     git push -u origin main

  {CYAN}Then move to Phase 1 Task 3 / 4:{RESET}
     state store schema (src/pipeline/state/) — pure local work, no containers
     then bootstrap/02_create_containers.sh — create the 3 LXD containers
     (not written yet — next task in the execution sequence)
""")


def main():
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    print(f"\n{CYAN}media-pipeline — Phase 1, Task 1: Repo & Folder Structure Scaffold{RESET}")
    print(f"Repo root : {repo_root}")
    print(f"Dry run   : {args.dry_run}")

    if not args.dry_run:
        repo_root.mkdir(parents=True, exist_ok=True)
    elif not repo_root.exists():
        warn(f"Repo root does not exist yet (dry-run, would be created): {repo_root}")

    create_dirs(repo_root, args.dry_run)
    create_packages(repo_root, args.dry_run)
    create_gitkeeps(repo_root, args.dry_run)
    create_files(repo_root, args.dry_run)

    if not args.dry_run:
        print_next_steps()


if __name__ == "__main__":
    main()
