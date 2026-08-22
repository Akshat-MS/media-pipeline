"""
Unit tests for src/pipeline/validation/ (thresholds.py, validators.py) —
Phase 1, Task 9.
"""

import pytest

from pipeline.validation.thresholds import (
    DEFAULT_THRESHOLDS,
    checks_for_stage,
    is_gate,
    load_thresholds,
)
from pipeline.validation.validators import (
    all_gates_passed,
    failed_advisories,
    failed_gates,
    validate_audio_bitrate,
    validate_audio_channels,
    validate_audio_loudness,
    validate_audio_peak,
    validate_audio_sample_rate,
    validate_duration_match,
    validate_output_integrity,
    validate_output_resolution,
    validate_render_fps,
    validate_sequence_mapping_coverage,
    validate_stt_wer,
    validate_sync_drift,
    validate_video_bitrate,
    validate_video_codec,
)


def test_load_thresholds_default_matches_constants():
    assert load_thresholds() == DEFAULT_THRESHOLDS


def test_load_thresholds_override_does_not_mutate_defaults():
    overridden = load_thresholds({"sync_drift_ms_max": 100})
    assert overridden["sync_drift_ms_max"] == 100
    assert DEFAULT_THRESHOLDS["sync_drift_ms_max"] == 80


def test_load_thresholds_rejects_unknown_key():
    with pytest.raises(ValueError):
        load_thresholds({"not_a_real_threshold": 1})


def test_is_gate_classification():
    assert is_gate("audio_loudness") is True
    assert is_gate("stt_wer") is False


def test_is_gate_unknown_check_raises():
    with pytest.raises(KeyError):
        is_gate("nonexistent")


def test_checks_for_stage_groups_correctly():
    checks = set(checks_for_stage("video_compose"))
    assert checks == {
        "sync_drift", "render_fps", "duration_match", "output_integrity",
        "output_resolution", "video_codec", "video_bitrate",
        "audio_channels", "audio_sample_rate", "audio_bitrate",
    }


@pytest.mark.parametrize(
    "validator_call,should_pass",
    [
        (lambda: validate_audio_loudness(-16.2), True),
        (lambda: validate_audio_loudness(-25.0), False),
        (lambda: validate_audio_peak(-2.0), True),
        (lambda: validate_audio_peak(0.5), False),
        (lambda: validate_stt_wer(0.08), True),
        (lambda: validate_stt_wer(0.99), False),
        (lambda: validate_sequence_mapping_coverage(0.95), True),
        (lambda: validate_sequence_mapping_coverage(0.01), False),
        (lambda: validate_sync_drift(45), True),
        (lambda: validate_sync_drift(500), False),
        (lambda: validate_duration_match(120500, 120400), True),
        (lambda: validate_duration_match(90000, 120000), False),
        (lambda: validate_output_integrity(0, 5_000_000), True),
        (lambda: validate_output_integrity(1, 0), False),
    ],
)
def test_individual_validators(validator_call, should_pass):
    result = validator_call()
    assert result.passed is should_pass


def test_render_fps_within_range_passes():
    ok = validate_render_fps(28.0)
    assert ok.passed is True


def test_render_fps_below_min_fails():
    low = validate_render_fps(15.0)
    assert low.passed is False


def test_render_fps_above_max_fails():
    """Revised behavior: a 60fps source must be DOWNSAMPLED to the fixed
    24-30fps delivery standard, not passed through — this is the direct
    replacement for the old adaptive 'inherit source fps' rule."""
    high = validate_render_fps(60.0)
    assert high.passed is False


def test_render_fps_boundary_values_pass():
    assert validate_render_fps(24.0).passed is True
    assert validate_render_fps(30.0).passed is True


def test_output_resolution_exact_match_passes():
    result = validate_output_resolution(1920, 1080)
    assert result.passed is True


def test_output_resolution_mismatch_fails():
    result = validate_output_resolution(1280, 720)
    assert result.passed is False


def test_video_codec_case_insensitive_match():
    assert validate_video_codec("H.264 High Profile").passed is True
    assert validate_video_codec("h.264 high profile").passed is True
    assert validate_video_codec("H.265").passed is False


def test_video_bitrate_within_range():
    assert validate_video_bitrate(10.0).passed is True
    assert validate_video_bitrate(5.0).passed is False
    assert validate_video_bitrate(15.0).passed is False


def test_audio_channels_match():
    assert validate_audio_channels("stereo").passed is True
    assert validate_audio_channels("Stereo").passed is True
    assert validate_audio_channels("mono").passed is False


def test_audio_sample_rate_exact_match():
    assert validate_audio_sample_rate(48000).passed is True
    assert validate_audio_sample_rate(44100).passed is False


def test_audio_bitrate_within_range():
    assert validate_audio_bitrate(224).passed is True
    assert validate_audio_bitrate(128).passed is False
    assert validate_audio_bitrate(320).passed is False


def test_new_output_standard_checks_are_all_gates():
    for check_name in [
        "output_resolution", "video_codec", "video_bitrate",
        "audio_channels", "audio_sample_rate", "audio_bitrate",
    ]:
        assert is_gate(check_name) is True, f"{check_name} should be a gate per Image 1 spec"


def test_gate_failure_blocks():
    results = [
        validate_audio_loudness(-16.1),  # pass, gate
        validate_sync_drift(150),         # FAIL, gate
    ]
    assert all_gates_passed(results) is False
    assert [r.check_name for r in failed_gates(results)] == ["sync_drift"]


def test_advisory_failure_does_not_block():
    results = [
        validate_audio_loudness(-16.0),          # pass, gate
        validate_sync_drift(10),                  # pass, gate
        validate_stt_wer(0.99),                     # FAIL, advisory
        validate_sequence_mapping_coverage(0.01),    # FAIL, advisory
    ]
    assert all_gates_passed(results) is True, "advisory failures must never block"
    assert len(failed_advisories(results)) == 2
    assert failed_gates(results) == []


def test_mixed_gate_and_advisory_failure():
    results = [
        validate_sync_drift(150),   # FAIL, gate
        validate_stt_wer(0.99),      # FAIL, advisory
    ]
    assert all_gates_passed(results) is False
    assert len(failed_gates(results)) == 1
    assert len(failed_advisories(results)) == 1
