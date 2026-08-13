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


def get_required_fps(
    source_fps: float | None, thresholds: dict[str, float] = DEFAULT_THRESHOLDS
) -> float:
    """
    Adaptive rule: rendered output must match/exceed the source video's own
    fps. Falls back to a fixed default only when there's no source video to
    inherit from (pure PPTX input).
    """
    if source_fps is not None:
        return source_fps
    return thresholds["render_fps_fallback"]


def validate_render_fps(measured_fps: float, required_fps: float) -> ValidationResult:
    passed = measured_fps >= required_fps
    return ValidationResult(
        "render_fps", passed, is_gate("render_fps"),
        measured_fps, required_fps,
        f"measured {measured_fps}fps, required >= {required_fps}fps",
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
