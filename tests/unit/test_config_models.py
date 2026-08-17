"""
Unit tests for src/pipeline/services/config/models.py — ADR-007 §3, §4.
"""

import copy

import pytest
from pydantic import ValidationError

from pipeline.services.config.models import StyleContract


def test_style_contract_validates_real_committed_file(real_contract_raw):
    contract = StyleContract.model_validate(real_contract_raw)
    assert contract.schema_version == "1.0.0"
    assert contract.artifact_type == "global_style_contract"
    assert contract.payload.theme_selected is None


def test_missing_mandatory_field_raises_with_field_path(real_contract_raw):
    broken = copy.deepcopy(real_contract_raw)
    del broken["payload"]["themes"]["blue"]["accent_marker"]

    with pytest.raises(ValidationError) as exc_info:
        StyleContract.model_validate(broken)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("payload", "themes", "blue", "accent_marker") for e in errors)


def test_unknown_field_is_rejected_not_silently_ignored(real_contract_raw):
    broken = copy.deepcopy(real_contract_raw)
    broken["payload"]["canvas"]["widht"] = 1920  # typo

    with pytest.raises(ValidationError) as exc_info:
        StyleContract.model_validate(broken)

    assert any(e["type"] == "extra_forbidden" for e in exc_info.value.errors())


@pytest.mark.parametrize("field_to_remove", ["redundant", "primary_channel"])
def test_palette_channel_with_neither_signal_is_rejected(real_contract_raw, field_to_remove):
    broken = copy.deepcopy(real_contract_raw)
    # state_a only ever has "redundant"; removing it (a no-op for
    # "primary_channel" on this entry) still exercises the "neither
    # present" case correctly since state_a never had primary_channel.
    broken["payload"]["palette_roles"]["channels"]["state_a"].pop(field_to_remove, None)

    if field_to_remove == "redundant":
        with pytest.raises(ValidationError, match="must declare either"):
            StyleContract.model_validate(broken)
    else:
        # state_a never had primary_channel — removing it is a no-op,
        # redundant is still present, so this must still pass.
        StyleContract.model_validate(broken)


def test_palette_channel_with_only_primary_channel_is_valid(real_contract_raw):
    # focus_attention only has primary_channel, no redundant — must pass.
    contract = StyleContract.model_validate(real_contract_raw)
    channel = contract.payload.palette_roles.channels["focus_attention"]
    assert channel.redundant is None
    assert channel.primary_channel == "glow_or_scale_pulse"


def test_type_styles_picks_relative_variant_for_math_subscript(real_contract_raw):
    from pipeline.services.config.models import TypeStyleRelative

    contract = StyleContract.model_validate(real_contract_raw)
    style = contract.payload.type_styles["math_subscript"]
    assert isinstance(style, TypeStyleRelative)
    assert style.size_em == 0.62


def test_type_styles_picks_absolute_variant_for_most_entries(real_contract_raw):
    from pipeline.services.config.models import TypeStyleAbsolute

    contract = StyleContract.model_validate(real_contract_raw)
    style = contract.payload.type_styles["h1"]
    assert isinstance(style, TypeStyleAbsolute)
    assert style.size_px == 60


def test_math_variable_has_both_absolute_sizing_and_style(real_contract_raw):
    """Regression test — math_variable has step/size_px (absolute shape)
    AND a 'style' field, which TypeStyleAbsolute didn't originally allow.
    Caught by running the model against the real file during
    implementation; this pins the fix."""
    from pipeline.services.config.models import TypeStyleAbsolute

    contract = StyleContract.model_validate(real_contract_raw)
    style = contract.payload.type_styles["math_variable"]
    assert isinstance(style, TypeStyleAbsolute)
    assert style.style == "italic"
    assert style.step == 0


@pytest.mark.parametrize("bad_version", ["1.0", "v1.0.0", "1.0.0.0", "latest", ""])
def test_schema_version_rejects_malformed_semver(real_contract_raw, bad_version):
    broken = copy.deepcopy(real_contract_raw)
    broken["schema_version"] = bad_version

    with pytest.raises(ValidationError):
        StyleContract.model_validate(broken)


@pytest.mark.parametrize("field", ["video_bitrate_mbps", "audio_bitrate_kbps"])
def test_output_encode_bitrate_must_be_a_pair(real_contract_raw, field):
    broken = copy.deepcopy(real_contract_raw)
    broken["payload"]["output_encode"][field] = [8, 10, 12]  # 3 values, not a pair

    with pytest.raises(ValidationError, match="min, max"):
        StyleContract.model_validate(broken)


def test_list_level_2_has_stroke_px_level_3_size_px_is_a_pair(real_contract_raw):
    contract = StyleContract.model_validate(real_contract_raw)
    assert contract.payload.lists.level_2.stroke_px == 2
    assert contract.payload.lists.level_3.size_px == [10, 2]
