# Quality & Validation Thresholds

**Register:** numeric gates applied to pipeline output.
**Origin:** section 1.6 of the Phase 1 foundation document, extracted during
the docs restructure. Content unchanged.

> **Relationship to the Layer 0 register.** The encode-related values here
> overlap `layer0-requirements.md` TGT-003…008, which were derived later from
> competitive analysis. Where the two disagree, **TGT owns the value** — see
> the ownership table in `docs/README.md`. Config Mgmt design question 5 will
> settle whether these reference TGT or are reconciled into it.

> **Not yet implemented:** VGR-06 (text-render QC) and VGR-07 (content
> coverage) from `visual-grammar.md` owe entries in
> `src/pipeline/validation/thresholds.py` and `validators.py` once Sequence
> Mapping and Rendering exist to produce something checkable.

**REVISED v2** (post-Phase-1, during Phase 2 kickoff): fixed render fps range (24-30fps) REPLACES the earlier adaptive "inherit source fps" rule — the pipeline enhances quality to a standard, it does not just pass through whatever the source happened to be. Full delivered-output spec added (resolution, codec, bitrate, audio format) — all gates, all implemented and tested in `validation/thresholds.py` + `validators.py`.

## Concrete Design

Numeric, non-negotiable gates enforced automatically after each relevant stage — a stage that fails validation does not get marked `completed`, blocking downstream stages per the resumability design in 1.4.

| Metric | Threshold | Enforced After Stage |
| --- | --- | --- |
| **Audio/video sync drift** | ≤ **80 ms** absolute offset at any alignment checkpoint | Align, Video Compose |
| **Render output frame rate** | **FIXED** **24-30 fps** — output is normalized into this range regardless of source fps (a 60fps source is downsampled, a 15fps source is upsampled) | Video Compose |
| **Output resolution** | **1920×1080**, exact match | Video Compose |
| **Video codec/profile** | **H.264 High Profile** | Video Compose |
| **Video bitrate** | **8-12 Mbps** | Video Compose |
| **Audio channels** | **Stereo** | Video Compose |
| **Audio sample rate** | **48 kHz**, exact match | Video Compose |
| **Audio bitrate** | **192-256 kbps** | Video Compose |
| **Audio mean volume** | ≈ **-16 LUFS** integrated (EBU R128, ±1.0 tolerance) | Audio Preprocessing |
| **Audio peak ceiling** | ≤ **-1.0 dBFS** true peak | Audio Preprocessing |
| **STT word error rate (WER)** | **ADVISORY** ≤ **12%** on the reference sample set | Transcript Alignment |
| **Sequence Mapping coverage** | **ADVISORY** ≥ **90%** *(untuned placeholder)* of manifest elements mapped | Sequence Mapping |
| **Final output validation** | `ffprobe` exit code 0, duration within **±200ms** of expected, no corrupt/zero-byte output | Video Compose |

**What these mean, in plain terms:**

- **Audio/video sync drift** — the time gap between when something is *said* in the narration and when the matching visual appears on screen. Human perception starts noticing desync above roughly 100ms, so 80ms is the outer edge of "acceptable," not a target to hover near.
- **Render output frame rate — fixed standard (revised)**: the pipeline's job is to *enhance* video quality to a consistent delivery bar, so output is normalized into 24-30fps regardless of what the source provided — never a simple pass-through. This directly replaces the earlier "always ≥ source fps" adaptive rule, which would have let a low-quality source silently stay low-quality.
- **Delivered-output standard** (resolution, codec, bitrate, audio format) — sourced directly from a technical spec table the team defined for what a finished, enhanced lecture video should look like. All treated as hard gates, not suggestions, since they define what "enhanced" actually means for this product.
- **STT WER / Sequence Mapping coverage** — both advisory: logged, but don't block a stage from completing, since blocking on model accuracy while STT/mapping logic is still being tuned would be counterproductive. A failing gate always blocks; even every advisory failing simultaneously never does.

> Gate values are calibrated to catch real defects without blocking early progress on marginal cases — the two advisory thresholds in particular are meant to be tuned once real modules produce real accuracy numbers to tune against, not treated as immutable law. The delivered-output spec (resolution/codec/bitrate/audio format), by contrast, is a fixed product standard, not something expected to loosen over time.

## Trade-offs & Edge Cases

- **80ms sync drift is a compromise**: tightening to broadcast-grade (±40ms) will cost real debugging time once Sequence Mapping/Video Compose are being built.
- **Fixed fps range means real transcoding work, not just measurement** — Video Compose must actually normalize a source's native fps into range (interpolate up, downsample down), not just check a number after the fact. This is now a real requirement on that module's design, not only a validation concern.
- **VFR (variable frame rate) sources**: validate against `ffprobe -select_streams v -show_entries frame=pts_time` rather than naive frame count diffing.
- **WER threshold is model-dependent** — `faster-whisper` base/small models will sit near the 12% ceiling on noisy source audio; this is advisory precisely because of that variability.
- **Sequence Mapping coverage threshold (90%) is an untuned placeholder** — no real number existed for this anywhere prior; flagged honestly in the code rather than presented as settled.

> **See also:** `docs/visual_grammar_requirements.md` — a standing reference for *generation-time* behavioral requirements (camera movement, animation layering, narration-bound pacing, content coverage) that Phase 4 (Sequence Mapping) and Phase 5 (Rendering & Composition) design work must account for. Distinct from this section: 1.6 validates the output file after the fact; that document shapes how content gets generated in the first place.

## Claude Code Implementation Spec

*Spec file: `quality-thresholds.py`*
```

# Task 9 (DONE — actually built and tested, 87 passing tests):


# src/pipeline/validation/thresholds.py
DEFAULT_THRESHOLDS = {
    "audio_loudness_target_lufs": -16.0,
    "audio_peak_ceiling_dbfs": -1.0,
    "stt_wer_max": 0.12,
    "sequence_mapping_coverage_min": 0.90,   # untuned placeholder
    "sync_drift_ms_max": 80,
    "duration_tolerance_ms": 200,
    # Delivered-output standard (REVISED — replaces the old adaptive-fps
    # rule; sourced from the team's output-quality spec table):
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

def load_thresholds(overrides: dict | None = None) -> dict:
    # merges overrides onto DEFAULT_THRESHOLDS, rejects unknown keys
    ...

CHECKS = {
    "audio_loudness":            {"type": "gate",     "stage": "audio_preprocessing"},
    "audio_peak_ceiling":        {"type": "gate",     "stage": "audio_preprocessing"},
    "stt_wer":                   {"type": "advisory", "stage": "transcript_alignment"},
    "sequence_mapping_coverage": {"type": "advisory", "stage": "sequence_mapping"},
    "sync_drift":                {"type": "gate",     "stage": "video_compose"},
    "render_fps":                {"type": "gate",     "stage": "video_compose"},
    "duration_match":            {"type": "gate",     "stage": "video_compose"},
    "output_integrity":          {"type": "gate",     "stage": "video_compose"},
    "output_resolution":         {"type": "gate",     "stage": "video_compose"},
    "video_codec":               {"type": "gate",     "stage": "video_compose"},
    "video_bitrate":             {"type": "gate",     "stage": "video_compose"},
    "audio_channels":            {"type": "gate",     "stage": "video_compose"},
    "audio_sample_rate":         {"type": "gate",     "stage": "video_compose"},
    "audio_bitrate":             {"type": "gate",     "stage": "video_compose"},
}


# src/pipeline/validation/validators.py — one function per check, e.g.:
def validate_render_fps(measured_fps: float, thresholds=DEFAULT_THRESHOLDS):
    # FIXED range check (revised) — normalizes into [24, 30], no longer
    # inherits/passes through the source's own fps
    fps_min, fps_max = thresholds["render_fps_min"], thresholds["render_fps_max"]
    passed = fps_min <= measured_fps <= fps_max
    return ValidationResult("render_fps", passed, is_gate("render_fps"), ...)


# ...plus validate_output_resolution, validate_video_codec,

# validate_video_bitrate, validate_audio_channels,

# validate_audio_sample_rate, validate_audio_bitrate — same pattern.

def all_gates_passed(results: list) -> bool:
    # True only if every GATE-type result passed; advisory failures
    # never affect this, even if every advisory fails simultaneously.
    return all(r.passed for r in results if r.is_gate)


# Each Stage.validate_output() (from 1.3's Stage protocol) calls the

# relevant validator(s) and returns pass/fail with a structured reason —

# failed validation sets job_stages.status = 'failed', not 'completed'.

# Real dependencies used: pydantic, jiwer (WER), ffmpeg-python.
```
