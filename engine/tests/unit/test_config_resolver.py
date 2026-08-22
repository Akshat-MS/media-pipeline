"""
Unit tests for src/pipeline/services/config/resolver.py — ADR-007 §2, §6, §7.
"""

import logging

import pytest

from pipeline.services.config.resolver import (
    KNOWN_THEMES,
    ThemeResolutionError,
    resolve_theme,
)


def test_defaults_to_navy_when_nothing_is_set(real_contract, monkeypatch):
    monkeypatch.delenv("PIPELINE_STYLE_THEME", raising=False)
    resolved = resolve_theme(real_contract)
    assert resolved.theme == "navy"


def test_cli_theme_argument_is_used(real_contract):
    resolved = resolve_theme(real_contract, cli_theme="blue")
    assert resolved.theme == "blue"


def test_env_var_used_when_no_cli_arg(real_contract, monkeypatch):
    monkeypatch.setenv("PIPELINE_STYLE_THEME", "green_dark")
    resolved = resolve_theme(real_contract)
    assert resolved.theme == "green_dark"


def test_cli_arg_beats_env_var(real_contract, monkeypatch):
    monkeypatch.setenv("PIPELINE_STYLE_THEME", "green_dark")
    resolved = resolve_theme(real_contract, cli_theme="blue")
    assert resolved.theme == "blue"


def test_contract_field_used_when_no_cli_or_env(real_contract, monkeypatch):
    monkeypatch.delenv("PIPELINE_STYLE_THEME", raising=False)
    contract_with_theme = real_contract.model_copy(
        update={"payload": real_contract.payload.model_copy(update={"theme_selected": "blue"})}
    )
    resolved = resolve_theme(contract_with_theme)
    assert resolved.theme == "blue"


def test_env_var_beats_contract_field(real_contract, monkeypatch):
    monkeypatch.setenv("PIPELINE_STYLE_THEME", "green_dark")
    contract_with_theme = real_contract.model_copy(
        update={"payload": real_contract.payload.model_copy(update={"theme_selected": "blue"})}
    )
    resolved = resolve_theme(contract_with_theme)
    assert resolved.theme == "green_dark"


def test_unknown_theme_name_raises_not_falls_back_to_navy(real_contract):
    with pytest.raises(ThemeResolutionError, match="navey"):
        resolve_theme(real_contract, cli_theme="navey")


def test_unknown_theme_error_names_its_source(real_contract):
    with pytest.raises(ThemeResolutionError, match="CLI argument"):
        resolve_theme(real_contract, cli_theme="not_a_real_theme")


def test_resolved_object_has_no_theme_branching_left(real_contract):
    resolved = resolve_theme(real_contract)
    assert not hasattr(resolved, "themes")
    assert hasattr(resolved, "canvas")
    assert hasattr(resolved, "palette_roles")


def test_resolved_values_actually_differ_by_theme(real_contract):
    navy = resolve_theme(real_contract, cli_theme="navy")
    blue = resolve_theme(real_contract, cli_theme="blue")
    assert navy.accent_marker != blue.accent_marker


@pytest.mark.parametrize("theme", KNOWN_THEMES)
def test_every_known_theme_resolves_successfully(real_contract, theme):
    resolved = resolve_theme(real_contract, cli_theme=theme)
    assert resolved.theme == theme


def test_winning_source_is_logged_when_sources_disagree(real_contract, monkeypatch, caplog):
    monkeypatch.setenv("PIPELINE_STYLE_THEME", "green_dark")
    with caplog.at_level(logging.INFO, logger="pipeline.services.config.resolver"):
        resolve_theme(real_contract, cli_theme="blue")

    assert any("blue" in record.message and "CLI argument" in record.message for record in caplog.records)


def test_no_log_line_when_only_one_source_is_set(real_contract, monkeypatch, caplog):
    monkeypatch.delenv("PIPELINE_STYLE_THEME", raising=False)
    with caplog.at_level(logging.INFO, logger="pipeline.services.config.resolver"):
        resolve_theme(real_contract, cli_theme="blue")

    assert len(caplog.records) == 0
