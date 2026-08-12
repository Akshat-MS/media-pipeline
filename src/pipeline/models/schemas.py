"""
Job-level schemas. Stage-level types (Artifact, StageManifest) live in
core/manifest.py, not here — this file only owns things scoped to a whole
job, not to a single stage's input/output.

Re-exports Artifact and StageManifest for convenience so callers that need
"everything schema-related" can import from one place, without this file
owning their definitions (core/manifest.py remains the single source of
truth for those two).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from pipeline.core.manifest import Artifact, StageManifest  # re-exported, not redefined

__all__ = ["JobConfig", "Artifact", "StageManifest"]


class JobConfig(BaseModel):
    """
    What's needed to submit a new job. Maps directly onto
    repository.create_job()'s parameters (Task 3) — the CLI (Task 7+)
    parses user input into one of these, then passes it straight through.
    """

    source_pptx_path: str
    source_video_path: str
    review_mode: Literal["auto", "manual"]
    schema_version: str = "1.0.0"
