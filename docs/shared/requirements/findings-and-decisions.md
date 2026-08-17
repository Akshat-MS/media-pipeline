# Findings & Open Decisions

**Register C (RC-00x)** — root-cause findings that change *how* something is
built, not *what* the target is. Plus **DEC** open decisions and **PROP**
proposals not yet adopted.

**Status:** RC adopted; DEC-001 and PROP-001 open.
**Provenance:** derived from competitive analysis of the original lecture, our
previous output, and the competitor's output (measurements via ffprobe /
volumedetect / frame sampling). Evidence is retained in
[`competitive-analysis.md`](competitive-analysis.md).

> These are the entries most easily lost, because they do not look like
> requirements. A root-cause finding prevents a whole class of wrong fix.

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

---

## ### DEC-001 — Word-timestamp source (blocks VGR-05)

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

---

## Machine-readable

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "findings_and_decisions",
  "generated_at": null,
  "source": "layer_0_competitive_analysis",
  "payload": {
    "root_cause_findings": [
      {
        "id": "RC-001",
        "finding": "internal_render_fps_distinct_from_export_fps",
        "owner": "render.html_build",
        "status": "adopted"
      },
      {
        "id": "RC-002",
        "finding": "competitor_pacing_masked_by_audio_bed",
        "owner": "sequence_mapping",
        "status": "adopted"
      },
      {
        "id": "RC-003",
        "finding": "asr_downsampled_audio_not_master",
        "owner": "align.audio_preprocessing",
        "status": "adopted"
      }
    ],
    "open_decisions": [
      {
        "id": "DEC-001",
        "item": "word_timestamp_source",
        "blocks": [
          "VGR-05"
        ],
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
        "decisions_required": [
          "countable_unit",
          "gate_or_advisory",
          "threshold_band"
        ],
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

## Related

- Numeric targets → [`delivery-targets.md`](delivery-targets.md)
- Behavioural rules → [`visual-grammar.md`](visual-grammar.md)
- Phase 1 numeric gates → [`quality-thresholds.md`](quality-thresholds.md)
