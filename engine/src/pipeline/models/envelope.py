"""
The wrapper every persisted MODULE OUTPUT artifact conforms to (manifest.json,
transcript.json, plan.json, etc. — once real modules exist).

Deliberately separate from StageManifest (core/manifest.py, Task 6):
StageManifest is pipeline-internal control-plane data (how stages talk to
the orchestrator) and already carries its own schema_version field — it
does not get wrapped in this envelope. SchemaEnvelope is for a module's
actual output content, which evolves independently per module over time
and needs the full envelope (including `generator`, to know which module
produced it) for real forward-compatibility.

Per Phase 1, item 1.5.
"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, field_validator

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class SchemaEnvelope(BaseModel):
    """
    Every persisted module-output file is one of these, serialized to JSON.
    `data` holds the module-specific payload — this class never inspects
    or validates what's inside `data`; only the envelope fields themselves.
    """

    schema_version: str
    generated_at: datetime
    generator: str          # e.g. "pipeline.modules.visual_deconstruction"
    data: dict

    @field_validator("schema_version")
    @classmethod
    def validate_semver(cls, value: str) -> str:
        if not SEMVER_PATTERN.match(value):
            raise ValueError(
                f"schema_version must be strict MAJOR.MINOR.PATCH semver, got {value!r}"
            )
        return value
