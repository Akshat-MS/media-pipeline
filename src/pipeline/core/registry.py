"""
The single place a stage's execution order and container assignment are
declared. Task 7's orchestrator imports STAGE_ORDER and calls
get_container_for_stage() — it should never hardcode a stage name or
container name anywhere else.

Deliberately empty of real entries right now (Phase 1, Task 6). Module
names are decided at implementation time (per the folder-structure
discussion), not guessed here. Populate this file — and only this file —
once a real module is built and wired up.
"""

from __future__ import annotations

# Ordered list of stage names, in execution sequence. A name appearing
# here does NOT imply a strictly linear chain — some stages depend on
# more than one predecessor (e.g. Sequence Mapping needs both Visual
# Deconstruction's and Transcript Alignment's output — a fork/join, not a
# straight line). STAGE_ORDER records valid execution order; the actual
# dependency graph belongs to the orchestrator (Task 7), not here.
STAGE_ORDER: list[str] = []

# stage_name -> container_name. Every entry here must correspond to a real,
# already-created LXD container (Task 4: pipeline-structure, pipeline-speech,
# pipeline-render — see infra/lxd/profiles/).
STAGE_CONTAINER_MAP: dict[str, str] = {}


def register_stage(stage_name: str, container_name: str, *, position: int | None = None) -> None:
    """
    Add a stage to the registry. Call this once, at the point a real
    module's stage is wired up — not speculatively for stages that don't
    exist yet.

    position: index to insert at in STAGE_ORDER (defaults to appending at
    the end). Use this if a new stage needs to be inserted mid-sequence
    rather than tacked on after everything else.
    """
    if stage_name in STAGE_CONTAINER_MAP:
        raise ValueError(f"stage {stage_name!r} is already registered")

    STAGE_CONTAINER_MAP[stage_name] = container_name
    if position is None:
        STAGE_ORDER.append(stage_name)
    else:
        STAGE_ORDER.insert(position, stage_name)


def get_container_for_stage(stage_name: str) -> str:
    """Look up which container a stage runs in. Raises if not registered —
    the orchestrator should never silently fall back to a default here."""
    try:
        return STAGE_CONTAINER_MAP[stage_name]
    except KeyError:
        raise KeyError(
            f"stage {stage_name!r} is not registered — check core/registry.py"
        ) from None


def is_known_stage(stage_name: str) -> bool:
    return stage_name in STAGE_CONTAINER_MAP
