"""
The single place a stage's execution order, dependencies, container
assignment, and review-gate status are declared. The orchestrator (Task 7)
imports from here — it should never hardcode a stage name, container name,
or dependency relationship anywhere else.

Deliberately empty of real entries right now. Module names are decided at
implementation time, not guessed here. Populate this file — and only this
file — once a real module is built and wired up.

Extended during Task 7 (orchestrator build) to add STAGE_DEPENDENCIES and
GATED_STAGES — Task 6's STAGE_ORDER alone can't express that Sequence
Mapping needs both Visual Deconstruction's AND Transcript Alignment's
output (a fork/join, not a straight chain); see the Phase 1 pipeline
diagram (Fig. 2).
"""

from __future__ import annotations

# Ordered list of stage names. Registration order IS execution order —
# register_stage() only appends a stage once its dependencies are already
# registered (enforced below), so iterating STAGE_ORDER top to bottom is
# always a valid topological order. This is what the orchestrator walks.
STAGE_ORDER: list[str] = []

# stage_name -> container_name. Every entry here must correspond to a real,
# already-created LXD container (Task 4: pipeline-structure, pipeline-speech,
# pipeline-render — see infra/lxd/profiles/).
STAGE_CONTAINER_MAP: dict[str, str] = {}

# stage_name -> list of stage names that must be COMPLETED before this
# stage can run. Most stages depend on exactly one predecessor; a stage
# with more than one entry is a join point (e.g. sequence_mapping depends
# on both visual_deconstruction and transcript_alignment).
STAGE_DEPENDENCIES: dict[str, list[str]] = {}

# Stages that sit at one of the three named review gates (Manifest Review,
# Plan Review, Final Review & Sync QC — see the Phase 1 architecture
# diagram). Only stages in this set produce a review_status of 'pending'
# (manual mode) or 'auto_approved' (auto mode) on the job_stages row;
# every other stage's review_status stays 'not_applicable'.
GATED_STAGES: set[str] = set()


def register_stage(
    stage_name: str,
    container_name: str,
    *,
    depends_on: list[str] | None = None,
    is_gate: bool = False,
) -> None:
    """
    Add a stage to the registry. Call this once, at the point a real
    module's stage is wired up — not speculatively for stages that don't
    exist yet.

    depends_on: stage names that must complete before this one can run.
    Every name listed must already be registered — this enforces that
    STAGE_ORDER stays a valid topological order as stages are added.

    is_gate: whether this stage sits at one of the three named review
    gates (per the architecture diagram) — determines whether its
    completion carries a real review_status or stays 'not_applicable'.
    """
    if stage_name in STAGE_CONTAINER_MAP:
        raise ValueError(f"stage {stage_name!r} is already registered")

    deps = depends_on or []
    for dep in deps:
        if dep not in STAGE_CONTAINER_MAP:
            raise ValueError(
                f"stage {stage_name!r} depends on {dep!r}, which is not registered yet — "
                "register dependencies before the stages that depend on them"
            )

    STAGE_CONTAINER_MAP[stage_name] = container_name
    STAGE_DEPENDENCIES[stage_name] = deps
    if is_gate:
        GATED_STAGES.add(stage_name)
    STAGE_ORDER.append(stage_name)


def get_container_for_stage(stage_name: str) -> str:
    """Look up which container a stage runs in. Raises if not registered —
    the orchestrator should never silently fall back to a default here."""
    try:
        return STAGE_CONTAINER_MAP[stage_name]
    except KeyError:
        raise KeyError(
            f"stage {stage_name!r} is not registered — check core/registry.py"
        ) from None


def get_dependencies(stage_name: str) -> list[str]:
    try:
        return STAGE_DEPENDENCIES[stage_name]
    except KeyError:
        raise KeyError(
            f"stage {stage_name!r} is not registered — check core/registry.py"
        ) from None


def is_gated_stage(stage_name: str) -> bool:
    return stage_name in GATED_STAGES


def is_known_stage(stage_name: str) -> bool:
    return stage_name in STAGE_CONTAINER_MAP


def reset_registry() -> None:
    """
    Clear all registered stages. Not used by application code — exists
    for tests that need a clean registry between test cases, since the
    module-level dicts/lists above are otherwise shared global state.
    """
    STAGE_ORDER.clear()
    STAGE_CONTAINER_MAP.clear()
    STAGE_DEPENDENCIES.clear()
    GATED_STAGES.clear()
