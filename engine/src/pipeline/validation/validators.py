"""
One function per quality check (Phase 1, item 1.6). Each takes a measured
value and returns a ValidationResult — never raises for a failing check,
since validation failure is an expected outcome, not an exceptional one
(same principle as Stage.validate_output() in core/stage_protocol.py,
Task 6).

Nothing here reads real audio/video files — these functions take already-
measured numbers as input (e.g. "here is the LUFS value ffmpeg reported"),
not file paths. Whichever module eventually runs ffprobe/ffmpeg to produce
those numbers is a separate concern (module-specific code, not built yet);
this module only judges numbers against thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.validation.thresholds import DEFAULT_THRESHOLDS, checks_for_stage, is_gate


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    is_gate: bool           # True = failing this blocks the stage; False = advisory only
    measured_value: float | int | str | None
    threshold: float | int | str | None
    message: str


def validate_audio_loudness(
    measured_lufs: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    target = thresholds["audio_loudness_target_lufs"]
    # Allow a small tolerance band around the target rather than requiring
    # an exact match — real audio will never hit -16.0 LUFS to the decimal.
    tolerance = 1.0
    passed = abs(measured_lufs - target) <= tolerance
    return ValidationResult(
        "audio_loudness", passed, is_gate("audio_loudness"),
        measured_lufs, target,
        f"measured {measured_lufs} LUFS, target {target} ±{tolerance}",
    )


def validate_audio_peak(
    measured_peak_dbfs: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    ceiling = thresholds["audio_peak_ceiling_dbfs"]
    passed = measured_peak_dbfs <= ceiling
    return ValidationResult(
        "audio_peak_ceiling", passed, is_gate("audio_peak_ceiling"),
        measured_peak_dbfs, ceiling,
        f"measured peak {measured_peak_dbfs} dBFS, ceiling {ceiling} dBFS",
    )


def validate_stt_wer(
    measured_wer: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    max_wer = thresholds["stt_wer_max"]
    passed = measured_wer <= max_wer
    return ValidationResult(
        "stt_wer", passed, is_gate("stt_wer"),
        measured_wer, max_wer,
        f"measured WER {measured_wer:.1%}, max {max_wer:.1%} (advisory — does not block)",
    )


def validate_sequence_mapping_coverage(
    measured_coverage: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    min_coverage = thresholds["sequence_mapping_coverage_min"]
    passed = measured_coverage >= min_coverage
    return ValidationResult(
        "sequence_mapping_coverage", passed, is_gate("sequence_mapping_coverage"),
        measured_coverage, min_coverage,
        f"measured coverage {measured_coverage:.1%}, min {min_coverage:.1%} (advisory — does not block)",
    )


def validate_sync_drift(
    measured_drift_ms: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    max_drift = thresholds["sync_drift_ms_max"]
    passed = abs(measured_drift_ms) <= max_drift
    return ValidationResult(
        "sync_drift", passed, is_gate("sync_drift"),
        measured_drift_ms, max_drift,
        f"measured drift {measured_drift_ms}ms, max {max_drift}ms",
    )


def validate_render_fps(
    measured_fps: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    """
    Fixed delivery standard (revised — supersedes the earlier adaptive
    "inherit source fps" rule): output must land within [render_fps_min,
    render_fps_max] regardless of the source's own frame rate. The
    pipeline's job is to enhance quality to a consistent delivery
    standard, not simply pass through whatever the source happened to be
    — a 60fps source gets downsampled, a 15fps source gets upsampled,
    both to land in range.
    """
    fps_min = thresholds["render_fps_min"]
    fps_max = thresholds["render_fps_max"]
    passed = fps_min <= measured_fps <= fps_max
    return ValidationResult(
        "render_fps", passed, is_gate("render_fps"),
        measured_fps, f"{fps_min}-{fps_max}",
        f"measured {measured_fps}fps, required {fps_min}-{fps_max}fps",
    )


def validate_duration_match(
    measured_duration_ms: float,
    expected_duration_ms: float,
    thresholds: dict[str, float] = DEFAULT_THRESHOLDS,
) -> ValidationResult:
    tolerance = thresholds["duration_tolerance_ms"]
    diff = abs(measured_duration_ms - expected_duration_ms)
    passed = diff <= tolerance
    return ValidationResult(
        "duration_match", passed, is_gate("duration_match"),
        measured_duration_ms, expected_duration_ms,
        f"measured {measured_duration_ms}ms, expected {expected_duration_ms}ms ±{tolerance}ms (diff {diff}ms)",
    )


def validate_output_integrity(ffprobe_exit_code: int, file_size_bytes: int) -> ValidationResult:
    passed = ffprobe_exit_code == 0 and file_size_bytes > 0
    return ValidationResult(
        "output_integrity", passed, is_gate("output_integrity"),
        f"exit={ffprobe_exit_code}, size={file_size_bytes}B", "exit=0, size>0B",
        "file is valid and playable" if passed else "ffprobe failed or file is empty/corrupt",
    )


# ── Delivered-output standard validators (Image 1) ──────────────────────
# All gates — the pipeline enhances quality, so these are non-negotiable
# delivery requirements, not advisory suggestions.

def validate_output_resolution(
    measured_width: int, measured_height: int,
    thresholds: dict[str, float] = DEFAULT_THRESHOLDS,
) -> ValidationResult:
    target_w = thresholds["output_resolution_width"]
    target_h = thresholds["output_resolution_height"]
    passed = measured_width == target_w and measured_height == target_h
    return ValidationResult(
        "output_resolution", passed, is_gate("output_resolution"),
        f"{measured_width}x{measured_height}", f"{target_w}x{target_h}",
        f"measured {measured_width}x{measured_height}, required {target_w}x{target_h}",
    )


def validate_video_codec(
    measured_codec: str, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    target = thresholds["video_codec"]
    passed = measured_codec.strip().lower() == str(target).strip().lower()
    return ValidationResult(
        "video_codec", passed, is_gate("video_codec"),
        measured_codec, target,
        f"measured {measured_codec!r}, required {target!r}",
    )


def validate_video_bitrate(
    measured_mbps: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    lo, hi = thresholds["video_bitrate_mbps_min"], thresholds["video_bitrate_mbps_max"]
    passed = lo <= measured_mbps <= hi
    return ValidationResult(
        "video_bitrate", passed, is_gate("video_bitrate"),
        measured_mbps, f"{lo}-{hi}",
        f"measured {measured_mbps}Mbps, required {lo}-{hi}Mbps",
    )


def validate_audio_channels(
    measured_channels: str, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    target = thresholds["audio_channels"]
    passed = measured_channels.strip().lower() == str(target).strip().lower()
    return ValidationResult(
        "audio_channels", passed, is_gate("audio_channels"),
        measured_channels, target,
        f"measured {measured_channels!r}, required {target!r}",
    )


def validate_audio_sample_rate(
    measured_hz: int, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    target = thresholds["audio_sample_rate_hz"]
    passed = measured_hz == target
    return ValidationResult(
        "audio_sample_rate", passed, is_gate("audio_sample_rate"),
        measured_hz, target,
        f"measured {measured_hz}Hz, required {target}Hz",
    )


def validate_audio_bitrate(
    measured_kbps: float, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> ValidationResult:
    lo, hi = thresholds["audio_bitrate_kbps_min"], thresholds["audio_bitrate_kbps_max"]
    passed = lo <= measured_kbps <= hi
    return ValidationResult(
        "audio_bitrate", passed, is_gate("audio_bitrate"),
        measured_kbps, f"{lo}-{hi}",
        f"measured {measured_kbps}kbps, required {lo}-{hi}kbps",
    )


# ── Stage-level orchestration helpers ───────────────────────────────────

def all_gates_passed(results: list[ValidationResult]) -> bool:
    """
    True only if every GATE-type result passed. Advisory failures never
    affect this — this is exactly what the orchestrator should call to
    decide whether a stage is allowed to be marked completed.
    """
    return all(r.passed for r in results if r.is_gate)


def failed_gates(results: list[ValidationResult]) -> list[ValidationResult]:
    return [r for r in results if r.is_gate and not r.passed]


def failed_advisories(results: list[ValidationResult]) -> list[ValidationResult]:
    return [r for r in results if not r.is_gate and not r.passed]
