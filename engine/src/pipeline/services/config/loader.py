"""
Loads the global style contract off disk.

Per ADR-007 §1: this file stays thin — read the path, parse JSON, check
schema_version and migrate forward if needed (§4), then hand off to
StyleContract for validation (§3). Theme resolution and override
precedence (§2, §7) are resolver.py's job, not this file's — nothing here
knows what a "theme" is.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import ValidationError

from pipeline.models.migrations import migrate_to_latest
from pipeline.services.config.models import EXPECTED_SCHEMA_VERSION, StyleContract

# global_style_contract.py -> config -> services -> pipeline -> src -> repo_root
_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CONTRACT_PATH = _REPO_ROOT / "res" / "config" / "style" / "global_style_contract.json"

# The one artifact type this loader knows about — deliberately not generic
# over artifact types, per ADR-007 §8. Also the schema_name key used by
# pipeline.models.migrations.
ARTIFACT_TYPE = "global_style_contract"

__all__ = ["ContractLoadError", "load_style_contract", "DEFAULT_CONTRACT_PATH"]


class ContractLoadError(Exception):
    """Raised when the style contract can't be read, parsed, migrated, or
    validated. Wraps the lower-level error with the contract path, since
    a bare pydantic/json error won't say which file it came from."""


def _default_path() -> Path:
    """Honors PIPELINE_STYLE_CONTRACT_PATH for tests, same convention as
    PIPELINE_DB_PATH in state/db.py — falls back to the committed contract
    at the repo root otherwise."""
    override = os.environ.get("PIPELINE_STYLE_CONTRACT_PATH")
    return Path(override) if override else DEFAULT_CONTRACT_PATH


def load_style_contract(path: Path | None = None) -> StyleContract:
    """
    Read, parse, migrate-if-needed, and validate the global style
    contract. Returns a validated, still-theme-agnostic StyleContract —
    call resolver.resolve_theme() on the result to get a rendering-ready
    config (ADR-007 §2, §6, §7).
    """
    contract_path = path if path is not None else _default_path()

    try:
        raw_text = contract_path.read_text()
    except FileNotFoundError:
        raise ContractLoadError(f"style contract not found at {contract_path}") from None
    except OSError as exc:
        raise ContractLoadError(f"could not read style contract at {contract_path}: {exc}") from exc

    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ContractLoadError(f"style contract at {contract_path} is not valid JSON: {exc}") from exc

    if "schema_version" not in raw:
        raise ContractLoadError(f"style contract at {contract_path} is missing 'schema_version'")

    if raw["schema_version"] != EXPECTED_SCHEMA_VERSION:
        try:
            raw = migrate_to_latest(ARTIFACT_TYPE, raw)
        except (KeyError, ValueError, RuntimeError) as exc:
            raise ContractLoadError(
                f"style contract at {contract_path} declares schema_version "
                f"{raw['schema_version']!r}, which this code does not expect "
                f"({EXPECTED_SCHEMA_VERSION!r}), and no migration path was found: {exc}"
            ) from exc

    try:
        return StyleContract.model_validate(raw)
    except ValidationError as exc:
        raise ContractLoadError(
            f"style contract at {contract_path} failed validation:\n{exc}"
        ) from exc
