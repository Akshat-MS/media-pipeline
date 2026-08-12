"""
The formal contract every pipeline stage must implement.

This is what lets the orchestrator (Task 7, not yet built) call any stage
identically — regardless of which module it actually is — because every
stage exposes the same two methods with the same shapes in and out.

Per Phase 1, item 1.3: stages are invoked as standalone CLI commands
(`pipeline run-stage <name> --input <path> --output <path>`) running inside
a container. This Protocol describes the Python-level shape a module's
stage implementation takes internally — the CLI wiring around it is a
separate, later concern once real modules exist.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pipeline.core.manifest import StageManifest


@runtime_checkable
class Stage(Protocol):
    """
    Every module's stage implementation must satisfy this shape:

        class VisualDeconstructionStage:
            name = "visual_deconstruction"

            def run(self, input_manifest: StageManifest) -> StageManifest:
                ...

            def validate_output(self, output_manifest: StageManifest) -> bool:
                ...

    No inheritance required — Protocol is structural (duck-typed), so any
    class with a matching `name` attribute and these two methods satisfies
    it. This is deliberate: stage implementations shouldn't be forced into
    an inheritance hierarchy just to be recognized as a valid stage.
    """

    name: str

    def run(self, input_manifest: StageManifest) -> StageManifest:
        """
        Perform this stage's transformation. Must be a pure function of
        input_manifest — no reaching into another stage's state, no shared
        mutable objects (per item 1.3). All cross-stage communication goes
        through StageManifest and file paths under /workdir.
        """
        ...

    def validate_output(self, output_manifest: StageManifest) -> bool:
        """
        Return True if output_manifest passes this stage's quality gates
        (per item 1.6 — numeric thresholds, checked here or delegated to
        validation/validators.py, not yet built). A False return means the
        orchestrator marks this stage attempt as failed, not completed —
        it does NOT raise; validation failure is an expected outcome, not
        an exceptional one.
        """
        ...
