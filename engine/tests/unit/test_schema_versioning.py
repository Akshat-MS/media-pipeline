"""
Unit tests for src/pipeline/models/envelope.py and migrations.py —
Phase 1, Task 8.
"""

from datetime import datetime, timezone

import pytest

from pipeline.models.envelope import SchemaEnvelope
from pipeline.models.migrations import (
    get_current_version,
    migrate_to_latest,
    register_migration,
)


def test_envelope_accepts_valid_semver():
    env = SchemaEnvelope(
        schema_version="1.0.0",
        generated_at=datetime.now(timezone.utc),
        generator="pipeline.modules.visual_deconstruction",
        data={"elements": []},
    )
    assert env.schema_version == "1.0.0"


@pytest.mark.parametrize("bad_version", ["1.0", "v1.0.0", "1.0.0.0", "latest", ""])
def test_envelope_rejects_malformed_semver(bad_version):
    with pytest.raises(Exception):
        SchemaEnvelope(
            schema_version=bad_version,
            generated_at=datetime.now(timezone.utc),
            generator="x",
            data={},
        )


def test_migration_chain_applies_in_order():
    @register_migration("visual_manifest", from_version="1.0.0", to_version="1.1.0")
    def _v1_to_v1_1(data):
        data = dict(data)
        data["element_type"] = data.pop("shape_type")
        data["schema_version"] = "1.1.0"
        return data

    @register_migration("visual_manifest", from_version="1.1.0", to_version="1.2.0")
    def _v1_1_to_v1_2(data):
        data = dict(data)
        data["confidence"] = 1.0
        data["schema_version"] = "1.2.0"
        return data

    assert get_current_version("visual_manifest") == "1.2.0"

    old = {"schema_version": "1.0.0", "shape_type": "arrow"}
    migrated = migrate_to_latest("visual_manifest", old)

    assert migrated["schema_version"] == "1.2.0"
    assert migrated["element_type"] == "arrow"
    assert "shape_type" not in migrated
    assert migrated["confidence"] == 1.0
    assert old["schema_version"] == "1.0.0", "original payload must not be mutated"


def test_already_current_payload_passes_through_unchanged():
    @register_migration("s", from_version="1.0.0", to_version="1.1.0")
    def _migrate(data):
        data = dict(data)
        data["schema_version"] = "1.1.0"
        return data

    current = {"schema_version": "1.1.0", "x": 1}
    result = migrate_to_latest("s", current)
    assert result == current


def test_missing_schema_version_raises():
    @register_migration("s", from_version="1.0.0", to_version="1.1.0")
    def _migrate(data):
        return data

    with pytest.raises(ValueError):
        migrate_to_latest("s", {"x": 1})


def test_version_newer_than_known_raises():
    @register_migration("s", from_version="1.0.0", to_version="1.1.0")
    def _migrate(data):
        data = dict(data)
        data["schema_version"] = "1.1.0"
        return data

    with pytest.raises(ValueError):
        migrate_to_latest("s", {"schema_version": "9.9.9"})


def test_gap_in_migration_chain_raises():
    @register_migration("s", from_version="1.0.0", to_version="1.1.0")
    def _migrate(data):
        data = dict(data)
        data["schema_version"] = "1.1.0"
        return data

    with pytest.raises(KeyError):
        migrate_to_latest("s", {"schema_version": "0.5.0"})  # no path from here


def test_unknown_schema_raises():
    with pytest.raises(KeyError):
        get_current_version("never_registered")


def test_migration_that_forgets_to_bump_version_is_caught():
    @register_migration("broken", from_version="1.0.0", to_version="1.1.0")
    def _broken(data):
        return dict(data)  # bug: doesn't update schema_version

    with pytest.raises(RuntimeError):
        migrate_to_latest("broken", {"schema_version": "1.0.0"})
