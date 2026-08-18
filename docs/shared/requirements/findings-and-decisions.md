# Findings & Open Decisions

**Register C (RC-00x)** — root-cause findings that change *how* something is
built, not *what* the target is. Plus **DEC** open decisions and **PROP**
proposals not yet adopted.

**Status:** RC adopted; DEC-001 **closed** (path A, forced alignment required);
PROP-001 **rejected**.
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
| RC-001 | **Internal render fps ≠ export fps.** Diagram pane rendered at 8 fps at source. | Export encoding cannot add motion detail that was never rendered. Raising export bitrate/fps will not fix choppiness — the fix is in the animation engine's frame generation. **Enforced by TGT-012 (gate, pre-render) and TGT-013 (advisory, post-render); TGT-002 alone cannot detect this.** | Rendering & Composing > HTML Build | adopted (was DIFF-007) |
| RC-002 | Competitor's audio bed masks silence; "draw-then-wait" structure may persist underneath | Do not treat competitor pacing as solved. Timing must be narration-bound at the *visual* layer, independent of audio design. | Sequence Mapping | adopted (was DIFF-002) |
| RC-003 | ASR-downsampled audio must not be reused as the master | Audio preprocessing must keep a 48 kHz stereo path separate from the 16 kHz ASR path | Transcript Alignment > Audio Preprocessing | adopted |

---

---

### DEC-001 — Word-timestamp source · **CLOSED**

VGR-05 requires word/phrase-level timestamps but did not say where they come
from. The source is **determined by the audio-path decision**:

| Audio path | Timestamp source | Cost |
|---|---|---|
| **(A) Clean original human recording** — *selected* | **Forced alignment** run against the audio | New component in Transcript Alignment — mandatory, not optional |
| (B) TTS re-synthesis | Engine-native word marks (Polly / ElevenLabs / Azure) | Free — but different voice, and all existing sync invalidated |

**Resolution — path A confirmed.** The professor's voice is retained and
narration timing is unchanged, per the project invariant. Narration is
confirmed human (pause-pattern match to the original).

**Consequence: forced alignment is a required component of Transcript
Alignment, not optional.**

| Decision | Detail |
|---|---|
| Word timings are produced for the **entire transcript**, unconditionally | `words[]` with `start_s` / `end_s` is a required output field. Once the aligner runs, every word is free; selective capture would cost more *and* put a decision inside a facts-only stage |
| **Phrase selection is a separate, later decision** | An aligner produces words; it cannot know that "from *Pᵢ* to *Rⱼ*" is one meaningful unit. Sequence Mapping selects the word span that binds to a visual action and derives start time and duration from it |
| Tooling | `faster-whisper` with `word_timestamps=True`, on the 16 kHz speech-recognition path — already a project dependency. WhisperX is the fallback if accuracy proves insufficient on notation-dense segments |
| Audio path | Alignment runs on the 16 kHz mono copy; the 48 kHz stereo master stays separate for delivery. Consistent with RC-003 |
| Accuracy | Forced alignment is typically ±20–50 ms, inside the 80 ms sync-drift gate |

**Worked example.** Narration: *"Request edge: from Pᵢ to Rⱼ."* Word timings
give every word a start and end. The beat that draws the request edge binds to
the span "from" → "j", giving a start of 13.35 s and a duration of **1.27 s** —
because that is how long the sentence took to say. **The duration is measured,
never chosen.** This is the concrete case against fixed animation durations in
the style contract.

**VGR-05 is unblocked.**

*Note retained: free word-marks were a genuine argument in favour of path B,
under-weighted when the audio path was first drafted. Path A wins on
voice-identity and sync-preservation grounds, but the trade-off was closer than
originally stated.*

### PROP-001 — Seconds-per-concept metric · **REJECTED**

**Origin:** DIFF-006 — read as "the competitor's clip is shorter and skips
content entirely."
**Intent was:** a tripwire so future "make it snappier" work could not buy
speed by silently dropping or rushing material.

**Rejected for two independent reasons.**

**1 · The origin observation was a measurement artifact.** The three durations
compared were not three versions of the same content:

| | Duration | What it actually is |
|---|---|---|
| Original | 120.1 s | The full lecture |
| Competitor | 61.0 s | A trimmed demo sample |
| Ours | 83.1 s | A trimmed demo sample, of different extent |

The competitor was not dropping content — they were showing a portion of it as
a sales sample, exactly as we did. Nothing about content loss can be inferred
from those durations. See the note on the duration row in
[`competitive-analysis.md`](competitive-analysis.md).

**2 · The failure it guards against is structurally precluded.** Two adopted
constraints remove the freedom entirely:

| | |
|---|---|
| **The project invariant** | Narration content *and timing* are fixed. Same voice, same words, same timing |
| **TGT-011** | Duration must match the full transcript, no silent trimming |

Together these make seconds-per-concept **not a free variable** — each concept
receives exactly the time the professor spent on it, inherited from the
original lecture. There is no mechanism by which speed could be bought, nobody
is shortening the lecture, and the constraints would not permit it.

**What remains covered elsewhere.** Visual-timing concerns are owned:

| Concern | Owned by |
|---|---|
| Visual timing does not track the words | VGR-05, word/phrase-level pacing |
| Something narrated has no visual | VGR-07, content coverage |
| Video shorter than the narration | TGT-011 |

**Retained rather than deleted**, per the governance rule — a deleted row
erases the reasoning, and this proposal is likely to be raised again.

*For the record, the three decisions it would have required were: the countable
unit for "concept" (suggested: DYNAMIC manifest asset); gate or advisory
(suggested: advisory, since pacing is partly taste); and a threshold band, to
be measured from the original lecture rather than guessed.*

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
        "blocks": [],
        "previously_blocked": [
          "VGR-05"
        ],
        "depends_on": "audio_path",
        "resolution": "path_a_clean_original",
        "consequence": "forced_alignment_required_component",
        "tooling": "faster_whisper_word_timestamps",
        "tooling_fallback": "whisperx",
        "alignment_audio_path": "16khz_asr_copy",
        "word_timings_scope": "entire_transcript_unconditional",
        "phrase_selection_owner": "sequence_mapping",
        "status": "closed"
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
        "rejected_reason": "origin observation compared a full lecture against two trimmed demo samples; and the failure mode is precluded by the narration invariant plus TGT-011, which make seconds-per-concept inherited rather than free",
        "covered_instead_by": [
          "VGR-05",
          "VGR-07",
          "TGT-011"
        ],
        "status": "rejected"
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
