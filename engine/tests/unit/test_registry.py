"""
Unit tests for src/pipeline/core/registry.py — Phase 1, Tasks 6 and 7.
"""

import pytest

from pipeline.core import registry


def test_register_stage_basic():
    registry.register_stage("visual_deconstruction", "pipeline-structure")
    assert registry.STAGE_ORDER == ["visual_deconstruction"]
    assert registry.get_container_for_stage("visual_deconstruction") == "pipeline-structure"
    assert registry.get_dependencies("visual_deconstruction") == []
    assert registry.is_gated_stage("visual_deconstruction") is False


def test_register_stage_with_dependencies_and_gate():
    registry.register_stage("visual_deconstruction", "pipeline-structure")
    registry.register_stage("transcript_alignment", "pipeline-speech")
    registry.register_stage(
        "sequence_mapping", "pipeline-structure",
        depends_on=["visual_deconstruction", "transcript_alignment"],
        is_gate=True,
    )
    assert registry.get_dependencies("sequence_mapping") == [
        "visual_deconstruction", "transcript_alignment"
    ]
    assert registry.is_gated_stage("sequence_mapping") is True


def test_register_stage_rejects_duplicate():
    registry.register_stage("x", "pipeline-structure")
    with pytest.raises(ValueError):
        registry.register_stage("x", "pipeline-render")


def test_register_stage_rejects_unregistered_dependency():
    with pytest.raises(ValueError):
        registry.register_stage("child", "pipeline-render", depends_on=["nonexistent_parent"])


def test_get_container_for_unknown_stage_raises():
    with pytest.raises(KeyError):
        registry.get_container_for_stage("nonexistent")


def test_get_dependencies_for_unknown_stage_raises():
    with pytest.raises(KeyError):
        registry.get_dependencies("nonexistent")


def test_is_known_stage():
    assert registry.is_known_stage("x") is False
    registry.register_stage("x", "pipeline-structure")
    assert registry.is_known_stage("x") is True


def test_stage_order_preserves_registration_order():
    registry.register_stage("a", "pipeline-structure")
    registry.register_stage("b", "pipeline-speech")
    registry.register_stage("c", "pipeline-render", depends_on=["a", "b"])
    assert registry.STAGE_ORDER == ["a", "b", "c"]
