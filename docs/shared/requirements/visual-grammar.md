# Visual Grammar Requirements

**Status:** Standing reference — captured post-Phase-1, ahead of Phase 4
(Sequence Mapping) and Phase 5 (Rendering & Composition) design.

**Purpose:** these are behavioral/generation-time requirements for how the
pipeline decides *what* to show and *how* to animate it — distinct from
the numeric delivery thresholds in `1-lecture-alive-ai-foundation.html`
§1.6, which validate the *output file* after it's produced. Nothing here
is a number you check post-render; each item is a design constraint that
has to be built into Sequence Mapping's and Rendering & Composition's own
logic. Phase 4 and Phase 5 design conversations should explicitly work
through this table rather than starting from a blank page.

Two items (Text-render QC, Content coverage) also have a validation-gate
component — see the note under each.

---

| Item | Pipeline Module(s) | Description | Impact on Quality |
|---|---|---|---|
| **Semantic fidelity** | Sequence Mapping | Formal/technical notation (equations, labeled diagrams, precise terminology) visible in the source must never be dropped or simplified away for visual polish. This is a planning-time rule: it governs what content is allowed to survive into `plan.json` in the first place. | Directly determines whether the output is trustworthy as an educational artifact — losing notation for a cleaner-looking slide undermines the entire point of the video. |
| **Animation dimension layering** | Rendering &amp; Composition | Reveal, draw-in, camera movement, and dynamic state motion should compose together on a single element, not be treated as mutually exclusive effects picked one-at-a-time. | A layered approach reads as intentional and polished; picking only one effect per element tends to look flat or arbitrary by comparison. |
| **Camera movement is narration-driven** | Rendering &amp; Composition | Pan, zoom, and focus changes must be tied to what's currently being said in the narration — never decorative motion added for visual interest on its own. | Undirected camera motion is actively distracting in instructional content; narration-tied motion instead reinforces what the viewer should be attending to. |
| **Dynamic state motion** | Rendering &amp; Composition | Applies to every "stateful" concept (something that changes, accumulates, or transitions) — not just a special-cased few. Merges with pacing: e.g. staggered reveals, traveling-dot lines that trace a process as it's narrated. | Consistent motion treatment across all stateful content keeps the visual language coherent; inconsistent treatment reads as arbitrary/unfinished. |
| **Word/phrase-level pacing** | Sequence Mapping, Transcript Alignment | Visual changes must be bound to narration timing at the word/phrase level, not just "this clip plays during this segment." Requires Transcript Alignment to output word/phrase-level timestamps (not only segment-level) for Sequence Mapping to bind against. | This is the single biggest lever on perceived sync quality — coarse, clip-level timing is what makes generated video feel mechanically assembled rather than genuinely narrated. |
| **Text-render QC** | Rendering &amp; Composition *(+ new validation gate)* | Automated check for overlapping or clipped text layers, run before every export — not a manual visual spot-check. | Overlapping/clipped text is an immediately visible defect that undermines credibility even when everything else about the video is correct. |
| **Content coverage** | Sequence Mapping *(+ new validation gate)* | Full transcript coverage verified against the source transcript before export — every narrated point should have a corresponding visual, nothing narrated should be silently dropped from the plan. | Silent content loss is worse than a visible rendering defect — the viewer has no way to know something was cut, and the video becomes factually incomplete rather than just imperfect. |

---

## Cross-references

- **§1.6 Quality &amp; Validation Thresholds** (`1-lecture-alive-ai-foundation.html`) —
  the numeric, post-render gates (resolution, fps, bitrate, sync drift,
  etc.). Text-render QC and Content coverage above are expected to grow
  into real entries in `src/pipeline/validation/thresholds.py` /
  `validators.py` once Sequence Mapping and Rendering & Composition exist
  to produce something checkable — they are not yet implemented there.
- **Phase 4 (Sequence Mapping, Asset Library &amp; Execution Strategy)** —
  should explicitly design against: Semantic fidelity, Word/phrase-level
  pacing, Content coverage.
- **Phase 5 (Rendering &amp; Composition Engine)** — should explicitly
  design against: Animation dimension layering, Camera movement,
  Dynamic state motion, Text-render QC.
