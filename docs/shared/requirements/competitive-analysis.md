# Competitive Analysis — Evidence

**Provenance for the Layer 0 registers.** Measured with ffprobe, volumedetect
and frame sampling across three videos: the original lecture recording, our
previous output, and the competitor's output.

> This is **evidence, not requirement.** It is retained so any target can be
> traced back to what justified it. The requirements themselves live in
> [`delivery-targets.md`](delivery-targets.md),
> [`visual-grammar.md`](visual-grammar.md) and
> [`findings-and-decisions.md`](findings-and-decisions.md).

---

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

> ### ⚠ Durations are **not** comparable
>
> The three durations measure **different amounts of content**, deliberately:
>
> | | What it is |
> |---|---|
> | Original 120.1 s | The full lecture |
> | Competitor 61.0 s | A trimmed demo sample |
> | Ours 83.1 s | A trimmed demo sample, of different extent |
>
> The competitor was not dropping or rushing content — they trimmed a portion
> to show as a sample, exactly as we did. **Do not infer pacing, content
> coverage, or compression from this row.**
>
> This misreading already produced one bad requirement: PROP-001
> (seconds-per-concept), since rejected. See
> [`findings-and-decisions.md`](findings-and-decisions.md).
>
> Every other row *is* comparable — resolution, frame rate, codec, bitrate and
> loudness are properties of the encoding and do not vary with clip length.

Qualitative observations (visual grammar, dimensions used, semantic fidelity,
text QC, pacing, coverage) remain in
`Lecture_Alive_AI_CompetitiveAnalysis.xlsx` sheets 3 and 5.

---

## Client context

The client was **already satisfied** with the competitor's voice and animation
quality, and chose us on **correctness and cost**. Competitor production
quality is therefore the bar to **meet, not exceed** — and semantic accuracy
must never be traded for polish (VGR-01).

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

---

## Full workbook

All finalized tables, including the measured comparison and the qualitative
assessment, are in
[`../workbooks/design-decisions.xlsx`](../workbooks/design-decisions.xlsx).
