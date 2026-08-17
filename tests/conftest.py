"""
Shared pytest fixtures for the unit test suite.

Two things every test in this suite needs, which is why they live here
rather than being repeated per file:

1. A fresh, isolated SQLite database per test — never the real
   .pipeline/state.db, and never shared between tests (tests must not
   see each other's jobs).
2. A clean core.registry / models.migrations state per test — both are
   module-level global dicts (by design, see Tasks 6-8), which means
   without an explicit reset, one test registering a stage would leak
   into the next test and cause spurious failures or false passes.
"""

import sys
from pathlib import Path

# Make `pipeline` importable without requiring an editable install —
# tests should work the moment the repo is cloned, not depend on a setup
# step succeeding first.
SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import json

import pytest

from pipeline.core import registry
from pipeline.models import migrations
from pipeline.state import db, repository

CONTRACT_PATH = SRC_ROOT.parent / "res" / "config" / "style" / "global_style_contract.json"


@pytest.fixture
def real_contract_raw() -> dict:
    """The real committed style contract, as a plain dict — for tests that
    want to mutate a copy to construct a malformed variant."""
    return json.loads(CONTRACT_PATH.read_text())


@pytest.fixture
def real_contract():
    """The real committed style contract, already loaded and validated."""
    from pipeline.services.config.loader import load_style_contract

    return load_style_contract()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A Repository backed by a fresh, temporary SQLite file. Migrations
    are applied automatically (same as production, via db.connect())."""
    db_path = tmp_path / "test_state.db"
    monkeypatch.setenv("PIPELINE_DB_PATH", str(db_path))
    conn = db.connect(db_path)
    yield repository.Repository(conn)
    conn.close()


@pytest.fixture(autouse=True)
def _clean_global_registries():
    """
    Runs around EVERY test automatically (autouse=True) — clears the
    stage registry and migration registry before and after each test, so
    tests can freely call register_stage()/register_migration() without
    worrying about state from a previous test still being present.
    """
    registry.reset_registry()
    migrations.reset_migrations()
    yield
    registry.reset_registry()
    migrations.reset_migrations()
