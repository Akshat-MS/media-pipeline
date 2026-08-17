# Asset Deconstructor (Phase 2 — Visual Deconstruction) — Design Summary

Context for a new chat: continuing work on **Lecture Alive AI** (repo:
`media-pipeline`, github.com/Akshat-MS/media-pipeline, tag `phase1-complete`,
now public). Phase 1 (Foundations) is complete. This document captures every
decision made so far specifically for **Phase 2 / the `asset_deconstructor`
module**. Strategy/roadmap discussion (parallel-track execution plan, prompt
engineering track, etc.) is intentionally excluded — that's a separate thread.

---

## 1. Repo grounding (already built, do not redesign)

- `src/pipeline/core/registry.py` — `register_stage(stage_name, container_name,
  depends_on, is_gate)`, currently empty, populated one real entry at a time.
- `src/pipeline/core/manifest.py` — `StageManifest` / `Artifact`. `Artifact` is
  a **pointer** (file path + checksum), never inline content.
- Module folder convention: `src/pipeline/modules/<stage_name>/` containing
  `stage.py` + `models.py`.
- `docs/planning.md` confirms: this will be the **first real module** under
  `modules/`, running in the `pipeline-structure` LXD container (CPU-only, no
  GPU, lightweight parsing).
- Orchestrator, schema versioning (`envelope.py`/`migrations.py`), and 8
  validation gates already exist and are ready to receive this module's
  output — nothing needs to change there.

---

## 2. Naming — decided

- **Module/stage name:** `asset_deconstructor` (renamed from earlier
  "visual_deconstruction" placeholder), registered as
  `register_stage("asset_deconstructor", "pipeline-structure", ...)`.
- **Folder:** `src/pipeline/modules/asset_deconstructor/`
- **Interface:** `class AssetDeconstructor(Protocol)` — pluggable driver
  contract.
- **Concrete drivers (naming fixed from source design doc, which had a
  collision — both raster drivers were named `RasterHybridDriver`):**
  - `NativePPTXDriver` — build now
  - `RasterHybridOCRDriver` — dropped from design (see below)
  - `RasterHybridOCRVLMDriver` — deferred, not built now, interface must
    accommodate it later

---

## 3. Scope decision — confirmed by user

**The actual production input is a guaranteed `.pptx` file.** This resolves
the earlier open question about video-only/no-deck scenarios.

- `asset_deconstructor` is **slide-only** (PPTX). It does **not** parse the
  MP4. Video is a separate concern (narration audio + timing) feeding a later
  stage ("Transcript Alignment").
- This is a scope narrowing vs. the original blueprint wording for step 2.1
  ("PPTX parsing engine and MP4/video parsing engine") — worth reflecting in
  the blueprint doc when we update it.

---

## 4. Step 2.1 — Parsing/driver strategy — DECIDED

Evaluated against priorities Accuracy(P1) > Cost(P2) > Speed(P3) >
Complexity(P4) > Reliability(P5), on a CPU-only local machine.

| Approach | Verdict |
|---|---|
| **Native PPTX** (python-pptx / raw OOXML) | **Build now — sole v1 driver.** ~100% text accuracy, ~95–100% geometry, $0, <50ms/slide, fully local, no review gate needed. |
| Raster + OCR only | **Dropped.** Geometry-blind — cannot represent edges/diagrams at all. |
| Raster + OCR + classical CV | **Dropped/deprioritized.** Arrows are the common case in these decks, and classical CV (contour/Hough/color-mask) is weakest exactly on arrow direction — the highest-value field. Real accuracy ~70–85%, errors cluster on directionality. |
| Raster + OCR + VLM | **Deferred, not built now.** Best raster accuracy, but requires cloud (breaks local-first + CPU-only constraint) and a mandatory review gate. **Interface must be built to accept this later** as a fallback driver for any future no-deck scenario. |
| Pure end-to-end VLM | Rejected — worst structural discipline (hallucinates plausible-but-wrong edges), highest review burden. |

**Residual accuracy note:** Native PPTX geometry is ~100% for shape
position/size/text, but connector **direction** is only guaranteed if arrows
are true PowerPoint connector objects with stored begin/end refs. If they're
hand-drawn lines, direction still has to be inferred — same as raster, just
from clean vector coordinates instead of pixels.

---

## 5. Step 2.2 — Visual tree granularity — TENTATIVE, needs confirmation

Design doc's `assets[]` schema is effectively a **flat list with `parent_id`
for grouping**, not a deep recursive tree. This was noted as the doc's
apparent intent but has not been explicitly confirmed as a decision — **still
open** for the next session.

---

## 6. Step 2.3 — Input pipeline / normalization boundary — DECIDED (via §3)

Since scope is PPTX-only, there's no PPTX-vs-MP4 divergent-representation
problem to normalize — that concern from the original blueprint step 2.3 is
moot under the current scope. Normalization is just: OOXML shape tree →
`assets[]`.

---

## 7. Step 2.4 — Asset isolation / stable IDs — NOT YET DESIGNED

Flagged as the next real design task. One hard requirement has already
surfaced from downstream analysis (see §9): **element IDs must be stable
across re-runs**, or later alignment/sequence-mapping stages can't reliably
bind "this element" to "this audio timestamp" / "this animation." This is a
constraint on 2.4's design, not yet a full solution.

---

## 8. Step 2.5 — `manifest.json` schema — MOSTLY DRAFTED

From the reference design doc (dry-run tested against real Resource
Allocation Graph slides):

```
slide_id
metadata:
  extraction_path
  canvas_dimensions
  has_diagram
  diagram_implied
assets[]:
  element_id
  type
  shape_kind
  tag: STATIC | DYNAMIC
  semantic_type          # nullable — see boundary rule below
  bounding_box
  endpoints:
    anchor_element_id
    ...
  properties:
    text
    instance_count
    indent_level
    parent_id
    base_style
    highlight_style
```

**Task 1 / Task 3 boundary rule (decided, keep as-is):** `semantic_type` is
populated at extraction time **only** when geometry/typography alone
determines identity. Anything requiring narration context (e.g., is this
arrow a "request" or "assignment" edge?) stays `null` until Transcript
Alignment / Sequence Mapping resolves it downstream.

**Two schema gaps surfaced this session, not yet resolved:**

1. **Color-as-prior for connectors.** These decks use a real color
  convention (red = request edge, green = assignment edge). Decision so far:
  don't discard this signal, don't use it to override the boundary rule
  either — record it as a prior/confidence input (feeds a future
  `semantic_type_confidence` field) rather than setting `semantic_type`
  directly from color. Exact field shape not yet decided.
2. **Bullet ↔ diagram-element correspondence.** Some slides state their own
  edge list in text (e.g. "Request Edge: Pi ---> Rj"), which is a bullet that
  structurally *describes* a diagram element. No field currently captures
  this "describes/realizes" relationship — candidate: a `realizes:
  [element_id]` field on the text asset. Undecided whether this belongs in
  Phase 2 (structurally inferable at extraction) or Phase 3 (narration
  confirms it). **Open decision for next session.**

**Output contract clarification (not a redesign, just stated explicitly):**
`manifest.json` is the file an `Artifact` points to (path + checksum);
`StageManifest.metadata` stays for lightweight stage-level facts only. The
`assets[]` schema above is the manifest's content, wrapped by the existing
Stage protocol contract.

---

## 9. Grounding findings from sample media (still relevant, non-strategy)

From inspecting real sample slides/video (`Slide_2–5.png`,
`trimmed_rag.mp4`) before the `.pptx`-guaranteed scope was confirmed:

- Diagrams use a **consistent color convention**: red arrows = request
  edges, green arrows = assignment edges; dots inside resource rectangles =
  instance count (e.g., R2 has 2 dots, R4 has 4). This is the real-world
  source of the "color-as-prior" gap above.
- The sample video is a full-frame screen recording with **live annotation**
  (a highlight box that tracks the narration, moving bullet-to-bullet, plus
  a visible cursor). This is a rich timing signal but belongs to Phase 3
  (alignment/sequence), **not** to `asset_deconstructor` — noted so it isn't
  mistakenly pulled into Phase 2 scope later.
- These findings drove home why arrow-direction and instance-count are the
  hard/expensive fields — directly informing the 2.1 driver evaluation above.

---

## 10. Open items for the next session (in priority order)

1. Confirm 2.2 — flat-list-with-`parent_id` vs. real nested tree.
2. Design 2.4 — asset isolation strategy + stable element-ID scheme (this is
  now a hard downstream dependency, not just a nice-to-have).
3. Resolve the two 2.5 schema gaps — color-as-prior field shape, and whether
  `realizes` (bullet↔element correspondence) is Phase 2 or Phase 3.
4. Only after the above: write the actual `NativePPTXDriver` code against a
  real `.pptx` from this project (not the PNG/video samples).

---

## What to attach/link when starting the new chat

- **Repo link:** just restate `github.com/Akshat-MS/media-pipeline`
  (tag `phase1-complete`) — it's public now, so it can be re-cloned directly;
  no need to re-paste file contents.
- **Definitely re-attach:** `sketchmotion_design_doc_1_.html` — it's the
  primary reference doc this whole module design is built from and isn't in
  the repo.
- **Optional, only if picking up schema edge cases again:** the sample slide
  PNGs (`Slide_2–5.png`) — useful for re-grounding the color-convention /
  instance-count discussion in §9, but not required since the findings are
  already captured above.
- **Not needed for this module:** `trimmed_rag.mp4`, `animation_concepts_demo.html`,
  `Sample_video.mp4`, `Output_RA_1.mp4` — those fed the output-quality/strategy
  discussion, not Asset Deconstructor design. Skip them unless you want to
  revisit Phase 3/4 pacing or rendering topics in the new chat too.
- **The actual production `.pptx` for this deck**, once you have it — that's
  the one real artifact still missing, and item 4 above can't start without it.
