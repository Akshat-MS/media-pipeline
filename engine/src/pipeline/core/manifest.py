"""
Shared data shapes every pipeline stage's input and output must conform to.

These live in core/ (not models/) because they're tightly bound to the
Stage protocol itself (stage_protocol.py's method signatures reference
StageManifest directly) — this is the contract, not a general-purpose
schema. models/schemas.py owns job-level types (JobConfig) and imports
from here when it needs to wrap a manifest in the schema-versioning
envelope (Phase 1, item 1.5 — not yet built).

Per Phase 1, item 1.3: a stage is a pure transformation — one StageManifest
in, one StageManifest out. Nothing else should cross the boundary between
stages.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """
    A pointer to one file a stage produced — never the file's contents.
    Mirrors the artifacts table (Phase 1, item 1.2 / Task 3): artifact_type,
    file_path, and checksum are exactly what repository.upsert_artifact()
    expects to persist.
    """

    artifact_type: str          # e.g. "manifest", "plan_json", "final_video"
    file_path: str              # path under res/workdir/<job_id>/ or res/outputs/<job_id>/
    checksum: str                # sha256 hex digest of the file's current contents


class StageManifest(BaseModel):
    """
    The single input/output shape for every stage. A stage's run() method
    takes one of these in and returns one of these out — nothing else
    crosses the boundary between stages (no shared objects, no direct
    imports between stage modules, per item 1.3).
    """

    schema_version: str = "1.0.0"      # semver — see item 1.5 (envelope, not yet built)
    stage_name: str                    # which stage produced/consumes this manifest
    artifacts: list[Artifact] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    # Freeform per-stage data that doesn't warrant its own Artifact — e.g.
    # a stage might record {"detected_fps": 29.97} here. Keep this small;
    # anything file-shaped belongs in `artifacts`, not `metadata`.
