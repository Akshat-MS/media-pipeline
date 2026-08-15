"""
Numeric quality gates for Phase 1 (item 1.6), and which of them BLOCK a
stage from being marked completed (gates) versus which are logged but
non-blocking while accuracy is still being tuned (advisory).

These are Day 1 starting values — calibrated to catch real defects without
blocking early progress on marginal cases. Expected to be tuned in a later
phase against real fixture data, not treated as immutable law.

Override mechanism: load_thresholds() merges a dict of overrides onto the
defaults below. There's no pipeline.toml reader here yet — that's the
services/config/settings.py component (not yet built); when it exists, it
will call load_thresholds(overrides=parsed_toml_section) rather than this
module reading any file itself. This keeps threshold *values* separate
from *how they get configured*.
"""

from __future__ import annotations

from typing import Union

ThresholdValue = Union[float, int, str]

DEFAULT_THRESHOLDS: dict[str, ThresholdValue] = {
    "audio_loudness_target_lufs": -16.0,     # EBU R128 spoken-content standard
    "audio_peak_ceiling_dbfs": -1.0,
    "stt_wer_max": 0.12,
    "sequence_mapping_coverage_min": 0.90,   # placeholder — untuned, see note below
    "sync_drift_ms_max": 80,
    "duration_tolerance_ms": 200,

    # ── Delivered output standard (revised — supersedes the earlier
    #    adaptive-fps rule; see 1.6 REVISED v2 in the ADR). This is a
    #    fixed delivery-quality standard, not something that varies by
    #    source input: the pipeline's job is to ENHANCE video quality,
    #    so output must always meet this bar regardless of what was
    #    supplied, never just inherit/pass through a lower source spec.
    "output_resolution_width": 1920,
    "output_resolution_height": 1080,
    "render_fps_min": 24.0,
    "render_fps_max": 30.0,
    "video_codec": "H.264 High Profile",
    "video_bitrate_mbps_min": 8.0,
    "video_bitrate_mbps_max": 12.0,
    "audio_channels": "stereo",
    "audio_sample_rate_hz": 48000,
    "audio_bitrate_kbps_min": 192,
    "audio_bitrate_kbps_max": 256,
}
# NOTE on sequence_mapping_coverage_min: no real value for this existed in
# any prior discussion — 90% is a reasonable-sounding placeholder, not a
# number derived from anything concrete. Flagged here rather than silently
# presented as settled; revisit once Sequence Mapping is actually built
# and real coverage numbers exist to tune against.


def load_thresholds(overrides: dict[str, ThresholdValue] | None = None) -> dict[str, ThresholdValue]:
    """Merge overrides onto DEFAULT_THRESHOLDS. Never mutates the defaults."""
    merged = dict(DEFAULT_THRESHOLDS)
    if overrides:
        unknown = set(overrides) - set(DEFAULT_THRESHOLDS)
        if unknown:
            raise ValueError(f"unknown threshold key(s), check for typos: {sorted(unknown)}")
        merged.update(overrides)
    return merged


# ── Gate vs. advisory classification ────────────────────────────────────
# "gate"     -> failing this blocks the stage from being marked completed
#               (Orchestrator treats it the same as a stage execution failure).
# "advisory" -> failing this is logged but does NOT block; the stage still
#               completes. Used for accuracy-dependent checks where blocking
#               on e.g. 13% WER would be counterproductive while models are
#               still being tuned.
CHECKS: dict[str, dict[str, str]] = {
    "audio_loudness":            {"type": "gate",     "stage": "audio_preprocessing"},
    "audio_peak_ceiling":        {"type": "gate",     "stage": "audio_preprocessing"},
    "stt_wer":                   {"type": "advisory", "stage": "transcript_alignment"},
    "sequence_mapping_coverage": {"type": "advisory", "stage": "sequence_mapping"},
    "sync_drift":                {"type": "gate",     "stage": "video_compose"},
    "render_fps":                {"type": "gate",     "stage": "video_compose"},
    "duration_match":            {"type": "gate",     "stage": "video_compose"},
    "output_integrity":          {"type": "gate",     "stage": "video_compose"},
    # Added following the delivered-output standard (Image 1) — all
    # gates: the pipeline's job is to enhance quality, so these are
    # non-negotiable delivery requirements, not advisory suggestions.
    "output_resolution":         {"type": "gate",     "stage": "video_compose"},
    "video_codec":               {"type": "gate",     "stage": "video_compose"},
    "video_bitrate":             {"type": "gate",     "stage": "video_compose"},
    "audio_channels":            {"type": "gate",     "stage": "video_compose"},
    "audio_sample_rate":         {"type": "gate",     "stage": "video_compose"},
    "audio_bitrate":             {"type": "gate",     "stage": "video_compose"},
}


def is_gate(check_name: str) -> bool:
    try:
        return CHECKS[check_name]["type"] == "gate"
    except KeyError:
        raise KeyError(f"unknown check: {check_name!r}") from None


def checks_for_stage(stage_name: str) -> list[str]:
    return [name for name, meta in CHECKS.items() if meta["stage"] == stage_name]
