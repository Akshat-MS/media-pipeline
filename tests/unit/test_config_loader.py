"""
Unit tests for src/pipeline/services/config/loader.py — ADR-007 §1, §4.
"""

import json

import pytest

from pipeline.models.migrations import register_migration
from pipeline.services.config.loader import (
    DEFAULT_CONTRACT_PATH,
    ContractLoadError,
    load_style_contract,
)


def test_default_contract_path_points_at_the_committed_file():
    assert DEFAULT_CONTRACT_PATH.exists()
    assert DEFAULT_CONTRACT_PATH.name == "global_style_contract.json"


def test_load_style_contract_loads_the_real_file():
    contract = load_style_contract()
    assert contract.artifact_type == "global_style_contract"
    assert contract.source == "layer_1_manual"


def test_missing_file_raises_contract_load_error(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    with pytest.raises(ContractLoadError, match="not found"):
        load_style_contract(missing)


def test_malformed_json_raises_contract_load_error(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    with pytest.raises(ContractLoadError, match="not valid JSON"):
        load_style_contract(bad)


def test_missing_schema_version_key_raises(tmp_path):
    bad = tmp_path / "no-version.json"
    bad.write_text(json.dumps({"artifact_type": "global_style_contract", "payload": {}}))
    with pytest.raises(ContractLoadError, match="missing 'schema_version'"):
        load_style_contract(bad)


def test_future_version_with_no_migration_registered_raises(tmp_path):
    future = tmp_path / "future.json"
    future.write_text(
        json.dumps(
            {
                "schema_version": "9.9.9",
                "artifact_type": "global_style_contract",
                "generated_at": "2026-01-01T00:00:00Z",
                "source": "test",
                "payload": {},
            }
        )
    )
    with pytest.raises(ContractLoadError, match="no migration path was found"):
        load_style_contract(future)


def test_env_var_override_is_used_when_no_path_given(monkeypatch, tmp_path):
    missing = tmp_path / "only-reachable-via-env.json"
    monkeypatch.setenv("PIPELINE_STYLE_CONTRACT_PATH", str(missing))

    with pytest.raises(ContractLoadError, match=str(missing)):
        load_style_contract()


def test_explicit_path_argument_wins_over_env_var(monkeypatch, tmp_path):
    # If both an explicit path and the env var are set, the explicit
    # argument should be used — env var is only a fallback for when no
    # path is passed at all.
    monkeypatch.setenv("PIPELINE_STYLE_CONTRACT_PATH", "/should-not-be-read.json")
    contract = load_style_contract(DEFAULT_CONTRACT_PATH)
    assert contract.artifact_type == "global_style_contract"


def test_older_version_is_migrated_forward_then_validated(tmp_path, real_contract_raw):
    """An older contract on disk gets upgraded in memory via the
    migration chain (ADR-007 §4) — the file on disk is never touched, and
    the result still passes full StyleContract validation."""

    @register_migration("global_style_contract", from_version="0.9.0", to_version="1.0.0")
    def _migrate(data: dict) -> dict:
        data = dict(data)
        data["schema_version"] = "1.0.0"
        return data

    old_version_file = tmp_path / "old.json"
    old_payload = dict(real_contract_raw)
    old_payload["schema_version"] = "0.9.0"
    old_version_file.write_text(json.dumps(old_payload))

    original_bytes = old_version_file.read_text()
    contract = load_style_contract(old_version_file)

    assert contract.schema_version == "1.0.0"
    assert old_version_file.read_text() == original_bytes, "file on disk must never be mutated"
