# Layer 0 — Requirements Register

**Status:** complete (v1). Source of truth for what the final output must be.
**Provenance:** derived from `Lecture_Alive_AI_CompetitiveAnalysis.xlsx`
(measurements via ffprobe / silencedetect / volumedetect / frame sampling).

> **This is a target spec, not a comparison.** The three-way comparison is
> evidence and lives in the Evidence Appendix. What downstream layers consume
> is the requirement and its owner — not the gap that revealed it.

---

## How this file is organised (and why)

Layer 0 produced **two different species of requirement**. They are stored
separately because they are enforced by completely different mechanisms:

| Register | What it is | Enforced by | Consumed by |
|---|---|---|---|
| **A. Delivery targets** | Numeric properties of the finished file | Post-render validation gates | `validation/thresholds.py`, §1.6 |
| **B. Behavioural rules** | Generation-time design constraints | Built into module logic | Phase 4 / Phase 5 design |

A behavioural rule cannot be checked on an output file, and a delivery target
cannot be "designed into" a module. Flattening them into one list is what
causes requirements to be silently dropped at implementation time.

**Source-of-truth rule:** Register B is *indexed* here but **owned by**
`visual_grammar_requirements.md`. This file cites it; it does not restate it.
Edit the behavioural rules there, never here.

---

## Register A — Delivery Targets (numeric, post-render)

| ID | Property | Target | Owner (pipeline section) | Status |
|---|---|---|---|---|
| TGT-001 | Resolution | 1920x1080 | Rendering & Composing > Video Compose | adopted |
| TGT-002 | Export frame rate | 24–30 fps | Rendering & Composing > Video Compose | adopted |
| TGT-003 | Video codec/profile | H.264 High Profile | Rendering & Composing > Video Compose | adopted |
| TGT-004 | Video bitrate | 8–12 Mbps @ 1080p30 | Rendering & Composing > Video Compose | adopted |
| TGT-005 | Audio codec | AAC | Rendering & Composing > Video Compose | adopted |
| TGT-006 | Audio channels | Stereo | Transcript Alignment > Audio Preprocessing + Video Compose | adopted |
| TGT-007 | Audio sample rate | 48 kHz | Transcript Alignment > Audio Preprocessing *(do not reuse ASR-downsampled copy)* | adopted |
| TGT-008 | Audio bitrate | 192–256 kbps | Rendering & Composing > Video Compose | adopted |
| TGT-009 | Audio mean volume | −18 to −16 dB (~−16 LUFS) | Video Compose (mastering/normalization) | adopted |
| TGT-010 | Audio peak ceiling | −1.0 dB | Video Compose (mastering/normalization) | adopted |
| TGT-011 | Duration | Match full transcript length, no silent trimming | Sequence Mapping + Transcript Alignment | adopted |

**Note on TGT-011:** stated as a rule rather than a number because the target
is relative to each lecture's transcript. It is still post-render checkable,
so it stays in Register A.

---

## Register B — Behavioural Rules (generation-time)

**Owned by `visual_grammar_requirements.md`.** Indexed here for traceability
only — do not edit descriptions here.

| ID | Rule | Owner module(s) | Evidence | Status |
|---|---|---|---|---|
| VGR-01 | Semantic fidelity — never drop formal notation for polish | Sequence Mapping *(+ Asset Deconstruction: manifest must capture full notation)* | DIFF-004 | constraint |
| VGR-02 | Animation dimension layering — reveal + draw-in + camera + state motion compose, not either/or | Rendering & Composing > HTML Build | DIFF-001, DIFF-008 | adopted |
| VGR-03 | Camera movement is narration-driven, never decorative | Sequence Mapping + Rendering & Composing > HTML Build | DIFF-001 | adopted |
| VGR-04 | Dynamic state motion applies to every stateful concept; merges with pacing | Media Library + Sequence Mapping + HTML Build | DIFF-008 | adopted |
| VGR-05 | Word/phrase-level pacing — visual changes bind to word/phrase timestamps, not clip-level | Transcript Alignment (must emit word/phrase granularity) → Sequence Mapping | DIFF-002, DIFF-008 | adopted |
| VGR-06 | Text-render QC — automated overlap/clipping check before every export | Rendering & Composing > HTML Build *(+ new validation gate)* | DIFF-005 | adopted |
| VGR-07 | Content coverage — full transcript coverage verified before export | Sequence Mapping *(+ new validation gate)* | DIFF-006 | adopted |

VGR-06 and VGR-07 have a validation-gate component and will grow entries in
`thresholds.py` / `validators.py` once there is something checkable to run
them against.

---

## Register C — Root-Cause Findings

Findings that change *how* something is built, not *what* the target is.
These are the ones most easily lost, because they don't look like requirements.

| ID | Finding | Implication | Owner | Status |
|---|---|---|---|---|
| RC-001 | **Internal render fps ≠ export fps.** Diagram pane rendered at 8 fps at source. | Export encoding cannot add motion detail that was never rendered. Raising export bitrate/fps will not fix choppiness — the fix is in the animation engine's frame generation. | Rendering & Composing > HTML Build | adopted (was DIFF-007) |
| RC-002 | Competitor's audio bed masks silence; "draw-then-wait" structure may persist underneath | Do not treat competitor pacing as solved. Timing must be narration-bound at the *visual* layer, independent of audio design. | Sequence Mapping | adopted (was DIFF-002) |
| RC-003 | ASR-downsampled audio must not be reused as the master | Audio preprocessing must keep a 48 kHz stereo path separate from the 16 kHz ASR path | Transcript Alignment > Audio Preprocessing | adopted |

---

## Open Decisions / Proposed (not yet adopted)

### DEC-001 — Word-timestamp source (blocks VGR-05)

VGR-05 requires word/phrase-level timestamps but does not say where they come
from. The source is **determined by the Layer A audio decision**:

| Layer A path | Timestamp source | Cost |
|---|---|---|
| (A) Clean original human recording *(current default)* | **Forced alignment** (e.g. WhisperX) run against the audio | New component in Transcript Alignment — mandatory, not optional |
| (B) TTS re-synthesis | Engine-native word marks (Polly / ElevenLabs / Azure) | Free — but different voice, and all existing sync invalidated |

Narration is confirmed human (pause-pattern match to the original), so under
the current default **forced alignment is a required component** and must
appear in the Transcript Alignment design.

*Note: free word-marks are a genuine argument in favour of path B that was
under-weighted when Layer A was first drafted. Path A remains the default on
voice-identity and sync-preservation grounds, but the trade-off is closer than
originally stated.*

**To close:** confirm Layer A path, then register the alignment component
(and its model/tooling choice) as an owned item under Transcript Alignment.

### PROP-001 — Seconds-per-concept metric

**Origin:** DIFF-006 — competitor's clip is shorter and skips content entirely.
**Intent:** a tripwire so future "make it snappier" work cannot buy speed by
silently dropping or rushing material.

**Not a duplicate of VGR-07.** They catch different failures:

| | Measures | Catches |
|---|---|---|
| VGR-07 content coverage | binary — every narrated point has a visual | **omission** |
| PROP-001 seconds-per-concept | rate — screen time per concept | **rushing** |

A video can pass VGR-07 fully while showing each concept for 0.3s and being
incomprehensible. Both are needed.

**Three decisions required before adoption:**

1. **Countable unit for "concept."** Candidates: transcript sentence/phrase;
   manifest asset with `tag: DYNAMIC`; Layer 3 beat.
   *Suggested:* DYNAMIC manifest asset — already ID'd, countable, produced
   upstream, and corresponds to what actually appears on screen.
2. **Gate or advisory.** *Suggested:* **advisory**. Pacing is partly taste; a
   hard gate would fight legitimate variation between a definition slide and a
   worked example.
3. **Threshold band.** Leave `null` until **measured from the original
   lecture** — a real professor's pacing is the honest baseline. Material
   available: 120.1s original over a known concept set.

---

## Machine-readable slice

Wrapped in `SchemaEnvelope` per Phase 1's `models/envelope.py`.

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "layer0_requirements",
  "generated_at": null,
  "source": "layer_0_competitive_analysis",
  "payload": {
    "delivery_targets": [
      {"id": "TGT-001", "property": "resolution", "target": "1920x1080", "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-002", "property": "export_fps", "target": [24, 30], "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-003", "property": "video_codec_profile", "target": "h264_high", "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-004", "property": "video_bitrate_mbps", "target": [8, 12], "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-005", "property": "audio_codec", "target": "aac", "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-006", "property": "audio_channels", "target": 2, "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-007", "property": "audio_sample_rate_hz", "target": 48000, "owner": "align.audio_preprocessing", "status": "adopted"},
      {"id": "TGT-008", "property": "audio_bitrate_kbps", "target": [192, 256], "owner": "render.video_compose", "status": "adopted"},
      {"id": "TGT-009", "property": "audio_mean_lufs", "target": -16, "owner": "render.mastering", "status": "adopted"},
      {"id": "TGT-010", "property": "audio_peak_ceiling_db", "target": -1.0, "owner": "render.mastering", "status": "adopted"},
      {"id": "TGT-011", "property": "duration", "target": "match_transcript_no_trim", "owner": "sequence_mapping", "status": "adopted"}
    ],
    "behavioural_rules_ref": {
      "source_of_truth": "docs/visual_grammar_requirements.md",
      "ids": ["VGR-01","VGR-02","VGR-03","VGR-04","VGR-05","VGR-06","VGR-07"]
    },
    "root_cause_findings": [
      {"id": "RC-001", "finding": "internal_render_fps_distinct_from_export_fps", "owner": "render.html_build", "status": "adopted"},
      {"id": "RC-002", "finding": "competitor_pacing_masked_by_audio_bed", "owner": "sequence_mapping", "status": "adopted"},
      {"id": "RC-003", "finding": "asr_downsampled_audio_not_master", "owner": "align.audio_preprocessing", "status": "adopted"}
    ],
    "open_decisions": [
      {
        "id": "DEC-001",
        "item": "word_timestamp_source",
        "blocks": ["VGR-05"],
        "depends_on": "layer_a_audio_path",
        "if_clean_original": "forced_alignment_required",
        "if_tts": "engine_native_word_marks",
        "status": "open"
      }
    ],
    "proposed": [
      {
        "id": "PROP-001",
        "item": "seconds_per_concept_metric",
        "distinct_from": "VGR-07 (binary coverage vs rate)",
        "decisions_required": ["countable_unit", "gate_or_advisory", "threshold_band"],
        "suggested_unit": "manifest_asset_tag_dynamic",
        "suggested_enforcement": "advisory",
        "threshold_band": null,
        "threshold_source": "measure_from_original_lecture",
        "status": "proposed"
      }
    ]
  }
}
```

---

## Which layer consumes what

This routing is what lets Layer 1A pull only the style-relevant subset instead
of re-reading everything.

| Consumer | Pulls |
|---|---|
| **Layer 1A** (theme + entity vocabulary) | VGR-01, VGR-02, VGR-03, VGR-04 |
| **Layer 1B** (style contract JSON) | TGT-001…004 (canvas/encode block) |
| **Layer A** (audio) | TGT-005…010, RC-003, **DEC-001** |
| **Layer 3** (sequence/beats) | VGR-03, VGR-05, VGR-07, TGT-011, RC-002, DEC-001 |
| **Phase 5 render engine** | RC-001, VGR-02, VGR-06 |

---

## Governance

- IDs are **immutable and append-only**. Never renumber or reuse.
- Retire by `status` (`rejected` / `superseded_by: <ID>`), never by deleting a
  row — a deleted row leaves dangling citations and erases the reasoning.
- Status vocabulary: `adopted`, `constraint`, `proposed`, `rejected`,
  `superseded`.
- Register B descriptions are edited **only** in
  `visual_grammar_requirements.md`.

---

## Evidence Appendix

Raw three-way measurements retained as provenance. Not a requirement — kept so
any target can be traced to what justified it.

| Property | Original | Competitor | Ours |
|---|---|---|---|
| Duration | 120.1s | 61.0s | 83.1s |
| Resolution | 1920x1080 | 1920x1080 | 1280x720 |
| Frame rate | 25 fps | 30 fps | 8 fps |
| Video codec | H.264 High | H.264 Main | H.264 High |
| Video bitrate | 991 kbps | 14.3 Mbps | 26 kbps |
| Audio channels | Stereo | Stereo | Mono |
| Audio sample rate | 48 kHz | 48 kHz | 16 kHz |
| Audio bitrate | 253 kbps | 317 kbps | 50 kbps |
| Audio mean volume | −30.1 dB | −14.1 dB | −30.5 dB |
| Audio peak | −0.6 dB | 0.0 dB | −1.1 dB |

Qualitative observations (visual grammar, dimensions used, semantic fidelity,
text QC, pacing, coverage) remain in
`Lecture_Alive_AI_CompetitiveAnalysis.xlsx` sheets 3 and 5.
