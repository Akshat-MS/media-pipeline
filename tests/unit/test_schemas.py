"""
Unit tests for src/pipeline/models/schemas.py (JobConfig) — Phase 1, Task 6.
"""

import pytest

from pipeline.models.schemas import Artifact, JobConfig, StageManifest


def test_job_config_valid():
    jc = JobConfig(
        source_pptx_path="deck.pptx",
        source_video_path="lecture.mp4",
        review_mode="manual",
    )
    assert jc.schema_version == "1.0.0"  # default
    assert jc.review_mode == "manual"


def test_job_config_rejects_invalid_review_mode():
    with pytest.raises(Exception):
        JobConfig(
            source_pptx_path="a.pptx",
            source_video_path="a.mp4",
            review_mode="sometimes",
        )


def test_schemas_reexports_core_manifest_types():
    # Artifact / StageManifest should be the SAME classes as core.manifest's,
    # not redefined copies — this is the resolved Task 6 overlap.
    from pipeline.core.manifest import Artifact as CoreArtifact
    from pipeline.core.manifest import StageManifest as CoreStageManifest

    assert Artifact is CoreArtifact
    assert StageManifest is CoreStageManifest
