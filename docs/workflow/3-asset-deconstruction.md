# Layer 3 — Asset Deconstruction

**Scope:** per deck (one `.pptx` = one video) · **Prompt version:** v4
**Work status:** verified on one slide (V017 s02); deck run not yet made
**Emits:** `<video>.manifest.json` (build from) + `<video>.review.html` (decide with)
**Tooling:** `mpk deck extract` · `mpk review build`

> **Schema ownership.** The per-asset shape is owned by
> [`docs/shared/specs/asset-deconstructor-schema.md`](../shared/specs/asset-deconstructor-schema.md)
> §8. This file cites it and adds the deck-level wrapper. If the two disagree
> on an asset field, the spec wins and this file is the defect.

---

## 1 · What it does

Produces **what is in the deck, as structured data.** Facts only.

**The decision this layer owns:** none of consequence. That is deliberate —
this is the judgement-poor layer. Its job is to record what is present without
interpreting it.

| This layer answers | This layer does **not** answer |
|---|---|
| There is an arrow from shape A to shape B | Whether it means enqueue or dequeue |
| This text reads "BUFSIZE" and sits above that shape | Whether it is that shape's label |
| This rectangle contains four dots | That four dots means four instances |

**The boundary rule** (owned by the spec, restated because every prompt depends
on it): `semantic_type` is populated **only** where geometry or typography
alone determines identity. Anything needing narration context stays `null`,
with the visual signal recorded as a prior, and Layer 5 resolves it.

**Why the discipline matters.** The spec's driver evaluation rejected
end-to-end vision extraction specifically because it "hallucinates
plausible-but-wrong edges." A manifest that guesses is worse than one that
admits ignorance: a `null` gets resolved downstream, a wrong value gets built
on.

### Scope is the deck, not the slide

One `.pptx` in, one manifest out.

| | |
|---|---|
| **Why not per slide** | Splitting a deck manifest into per-slide files is a three-line script. Merging separately-produced files back into a coherent deck view is not — consistency across slides has to be re-decided, and that is exactly what a deck run gives you for free |
| **What it unlocks** | Chrome classified once instead of 13 times; recurring entities visible as a set; a deck-level inventory that Layer 6 needs and nothing else produces |
| **Deck sizes** | 13, 9, 4, 4, 4 — 34 slides total |

---

## 2 · The prompt to run

**Three steps. The first is a tool, the third has two options.**

| Step | How | Required? |
|---|---|---|
| **1** | `mpk deck extract` — OOXML shape tree for every slide | Yes, when the editable `.pptx` exists |
| **2** | A prompt — classify, tag, produce the manifest | Always |
| **3A** | `mpk review build` — the tool makes the review page | **Default** |
| **3B** | The prompt builds the review page itself | Optional, when you would rather not run a tool |

Geometry, text, indent levels, grouping and connector endpoints are all
explicit in the file. Reading them from a rendered picture converts known
values into guesses — most damagingly for connector direction, which the spec
identifies as the highest-error field. The verification run confirmed this:
both connectors resolved through `a:stCxn`/`a:endCxn` and `a:tailEnd`, giving
`direction_verified: true` with the evidence recorded.

---

### Step 1 — `mpk deck extract`

```
mpk deck extract V017.pptx --deck-id v017 --expect 5 -o v017.raw.json
```

Deterministic. Walks `<p:sp>`, `<p:pic>`, `<p:cxnSp>`, `<p:graphicFrame>` and
`<p:grpSp>` (descending into groups and resolving their transforms), and emits
raw geometry, text, colours, connector endpoints and `id_coverage`. `--expect`
warns when the slide count differs, so a truncated read is not silent.

**It reads visual lines, not just paragraphs.** PowerPoint uses `<a:br/>` soft
breaks freely, and `paragraph.text` joins them with `\x0b` — so three code
lines arrive as one string. The extractor emits `lines[]` alongside
`paragraphs[]` and flags the discrepancy. Layer 8 reveals *visual* lines, so
`lines[]` is the list that matters. On the V017 deck this fired on both code
blocks: 8 visual lines across 6 paragraphs.

Related commands, when the deck needs repair first:

| Need | Command |
|---|---|
| See what is in a deck | `mpk deck info V017.pptx` |
| A slide reconstructed at the wrong canvas size | `mpk deck normalize slide.pptx --like V017.pptx -o fixed.pptx` |
| Splice it into position | `mpk deck merge fixed.pptx --into V017.pptx --at 2 -o V017-full.pptx` |
| Check the result by eye | `mpk deck render V017-full.pptx -d render` |

---

### Step 2 — the prompt

```
INPUTS
  - context.md (standing project brief)
  - visual-grammar.md
  - v<deck>.raw.json from `mpk deck extract`, and/or the .pptx itself
  - optionally, rendered images of any slides you flag for eye-check
  - for step 3B only: tools/templates/slide-review.html

Use only: VGR-01. Ignore all other requirement entries. If a requirement
outside that list appears relevant, name it and stop — do not act on it.

YOU ARE RUNNING LAYER 3 — ASSET DECONSTRUCTION, over a whole deck.
Facts only. You are not deciding what anything means.

────────────────────────────────────────────────────────────────────
COVERAGE — do this first and report it
────────────────────────────────────────────────────────────────────
State the slide count you found. If it does not match what you were told
to expect, stop and say so — a truncated read is otherwise silent.

Walk EVERY shape on every slide, including:
  - <p:sp>            shapes and text boxes
  - <p:pic>           pictures
  - <p:cxnSp>         connectors
  - <p:graphicFrame>  TABLES, charts, SmartArt. A walk that only handles
                      <p:sp> silently misses every matrix in the deck.
                      For a table, capture the grid: rows, columns, and
                      each cell's text.
  - <p:grpSp>         groups. Descend into them, set parent_id on each
                      member, and note that member geometry is relative
                      to the group transform — record both the raw value
                      and the resolved absolute box.

Report ID COVERAGE per slide: the shape ids you captured, and any gaps in
the id sequence with your reading of why (deleted shape, group member,
not in spTree). Gaps are usually harmless, but an unreported gap can hide
a shape you missed, and nobody can see that later.

────────────────────────────────────────────────────────────────────
TEXT — VISUAL LINES, NOT JUST PARAGRAPHS
────────────────────────────────────────────────────────────────────
For every text asset record BOTH:
  paragraphs[] — {level, text} per <a:p>
  lines[]      — one entry per line a VIEWER SEES

They differ. PowerPoint uses <a:br/> soft breaks inside a paragraph, and
reading paragraph text alone joins them into one string — so
"lock = false; / do { / while tns(&lock);" arrives as a single line.
Layer 8 reveals visual lines, so lines[] is the list that matters, and a
merged line means three reveals collapse into one.
Where the two counts differ, raise a soft_line_breaks flag.

────────────────────────────────────────────────────────────────────
UNITS
────────────────────────────────────────────────────────────────────
Keep native EMU. Do NOT convert to pixels. State the unit in metadata.
Conversion is lossy, and Layer 5 re-lays-out every slide onto the style
contract's grid, so source pixel values do not survive into the output
anyway. What must survive exactly is text, topology and structure.

────────────────────────────────────────────────────────────────────
CHROME — classify once, per deck
────────────────────────────────────────────────────────────────────
Title bar, footer band, logo, slide-number placeholder and background
image repeat on most slides. Identify the recurring set ONCE as a
deck-level chrome_pattern, then reference it per slide rather than
re-deriving it. Re-classifying the same footer 13 times wastes effort and
invites the same element being tagged differently on different slides.

Background rasters are SUPERSEDED BY THE STYLE CONTRACT — record them,
never attempt to read their contents, and mark them so no later layer
tries to preserve them.

────────────────────────────────────────────────────────────────────
TAG — STATIC or DYNAMIC
────────────────────────────────────────────────────────────────────
  STATIC  = present for the whole slide, never animated: title, eyebrow,
            footer, background, logo, slide number, panel labels.
  DYNAMIC = content that will be revealed or animated: bullets, diagram
            nodes, connectors, table rows, code lines.
When genuinely unsure choose DYNAMIC and flag it. A STATIC element is
never considered again by later layers, so a wrong STATIC silently drops
content; a wrong DYNAMIC only costs a review.

────────────────────────────────────────────────────────────────────
ELEMENT IDS — MUST BE STABLE ACROSS RE-RUNS
────────────────────────────────────────────────────────────────────
Use <slide_id>_<ooxml_shape_id>, e.g. "v017_s02_14".
Never number sequentially by reading order — inserting one shape would
renumber everything after it, and every downstream binding to "this
element" would silently move to a different shape. If a shape has no
usable id, say so rather than inventing one.

────────────────────────────────────────────────────────────────────
SEMANTIC_TYPE — THE BOUNDARY RULE
────────────────────────────────────────────────────────────────────
Populate semantic_type ONLY where geometry or typography alone determines
it. "This is the title" is determined by position and size. "This arrow
is an enqueue edge" is NOT — it depends on the narration, and Layer 5
resolves it.

Where identity depends on context, leave semantic_type null and record:

    "semantic_type_prior": {
      "value": "shared_buffer",
      "basis": "prstGeom:flowChartPredefinedProcess; adjacent text reads
                'BUFSIZE'; middle node of both connectors",
      "confidence": null
    }

Leave confidence null. Do not invent a number for it.

COLOUR CONVENTIONS. Some decks use one — in the deadlock decks, red
arrows are request edges and green are assignment edges. Where a
convention is present, RECORD IT AS A PRIOR; never let it set
semantic_type. Where the resolved colours do not match any convention,
say so explicitly at deck level rather than silently omitting it. A
convention from one deck must not be assumed for another.

────────────────────────────────────────────────────────────────────
CONNECTORS
────────────────────────────────────────────────────────────────────
Direction is the single most error-prone field in this layer. Resolve it
from the XML, not by eye:
  - a:stCxn / a:endCxn give the connected shapes and connection sites
  - a:tailEnd / a:headEnd give which end carries the arrowhead
  - rot / flipH / flipV must be resolved before concluding anything about
    geometry; state how you resolved them

Set direction_verified true ONLY with that evidence, and record
direction_basis. Where the endpoints are not declared, infer the nearest
anchor, mark "inferred": true, set direction_verified false, and raise a
flag. Do not guess direction.

────────────────────────────────────────────────────────────────────
NOTATION IS VERBATIM (VGR-01)
────────────────────────────────────────────────────────────────────
Capture formal notation exactly — subscripts, arrows, set braces,
operators. "P = {P1, P2, ... Pn}" is not a simplification of anything; it
is the content. Never normalise, expand or tidy it. A lost subscript is a
factual error in an educational artifact.

────────────────────────────────────────────────────────────────────
RELATIONSHIP PRIORS — record, never assert
────────────────────────────────────────────────────────────────────
labels_prior — a text asset that appears to label a shape:
    "labels_prior": {"element_id": "v017_s02_12",
                     "basis": "text 'BUFSIZE'; box sits immediately above
                               and is horizontally centred on it"}
Without this, Layer 8 reveals a label and the shape it names as unrelated
elements at unrelated times.

realizes_prior — a bullet whose text describes a diagram element:
    "realizes_prior": {"element_ids": ["..."],
                       "basis": "text names Pi and Rj"}

Both are priors. Layer 5 confirms or rejects them against the narration.

────────────────────────────────────────────────────────────────────
FLAGS — a real field, not prose
────────────────────────────────────────────────────────────────────
Every asset carries flags[]. Each entry:
    {"code": "raster_content_unread",
     "note": "opaque raster; XML cannot say what is drawn inside",
     "severity": "info" | "warn" | "error",
     "needs_eye_check": true}
Use flags for: unread rasters, shapes that may render differently from
their type, inherited geometry, empty text boxes, rendered fields,
unverified connector direction, inferred endpoints, resolved transforms,
labels positioned outside their shape.
If a human needs to look at something, it must appear here — prose notes
are lost, flags are carried into the review page and into Layer 5.

────────────────────────────────────────────────────────────────────
SPEAKER NOTES
────────────────────────────────────────────────────────────────────
If the deck carries notes slides, capture their text per slide under
deck-level speaker_notes, and mark them explicitly as NOT NARRATION. The
narration comes from the recording, via Layer 4, and is fixed. Notes are
context only and must never be treated as script.

────────────────────────────────────────────────────────────────────
PRODUCE TWO THINGS, IN THIS ORDER
────────────────────────────────────────────────────────────────────

=== OUTPUT 1 — THE DECK MANIFEST (JSON) ===

{
  "deck_id": "v017",
  "metadata": { source_file, slide_count, canvas_dimensions {width,
                height, units:"EMU"}, extraction_path, colour_resolution },
  "deck": {
    "chrome_pattern": [ {element_role, appears_on_slides[], semantic_type,
                         note} ],
    "entity_inventory": [ {label, appears_on_slides[], element_ids[],
                           prior_semantic_type, note} ],
    "colour_convention": {"present": true|false, "mapping": {...},
                          "basis": "..."},
    "slide_index": [ {slide_id, title, element_count, has_diagram,
                      has_table} ],
    "speaker_notes": [ {slide_id, text, note: "NOT narration"} ],
    "id_coverage": [ {slide_id, captured_ids[], gaps[], reading} ],
    "consistency": "how recurring elements were treated across slides,
                    and anywhere you treated the same thing differently"
  },
  "slides": [ { slide_id, metadata, assets: [ ... per the spec §8, plus
                flags[], labels_prior, realizes_prior ] } ]
}

entity_inventory is what Layer 6 reads to build the topic's visual
vocabulary. It is the reason this layer runs per deck. Include every
labelled shape that appears on more than one slide, and every distinct
labelled shape even if it appears once.

=== OUTPUT 2 — THE REVIEW PAGE ===

STEP 3A (default) — do NOT produce the page. Stop after output 1 and say:
    run:  mpk review build <manifest>.json -o <deck>.review.html

STEP 3B (only when the run asks for it) — emit the slide-review template
VERBATIM with ONE substitution: replace the contents of the

    <script type="application/json" id="manifest"> … </script>

block with the manifest you just produced. Change nothing else — not the
CSS, not the JavaScript, not the markup.

DO NOT WRITE TABLE ROWS BY HAND, on either path. The page reads the
embedded manifest at load time and builds every row, flag, prior and
connector sentence from it. That is what makes it a view rather than a
second account: the table and the data are the same object, so they cannot
disagree. It is also why a 13-slide deck stays a small file.

If a fact should appear on the review page, it belongs in the manifest —
as a flag, a prior, or a deck-level field. Never add it to the markup.

Two checks before you finish 3B:
  - the embedded block is valid JSON on its own
  - it is the SAME manifest as output 1, not a summary of it

End with UNRESOLVED / ASSUMPTIONS / FLAGS. Write "none" if genuinely
empty.
```

---

## 3 · What it emits

| Form | What | For |
|---|---|---|
| **Build from** | `<video>.manifest.json` | Layers 5, 6 and 8; `asset_deconstructor` fixtures |
| **Decide with** | `<video>.review.html` — the template with the manifest embedded | You, approving a slide in under a minute |

**Two paths.** Step 3A has `mpk review build` fill the template; step 3B has
the prompt fill it. Same template, same page — pick per run.

The review page carries the manifest inside itself, in a
`<script type="application/json" id="manifest">` block, and renders it in the
browser at load time. So the page is a **view** of the data by construction —
the table cannot disagree with the JSON, because it *is* the JSON.

| Consequence | |
|---|---|
| Nothing to install or run | Open the file; it renders |
| Cannot drift | The markup is generated from the embedded manifest every load |
| Self-contained | One file to keep, attach, or send. The JSON can be lifted back out of it |
| To change what the page shows | Change the manifest, never the markup |

**One owner per page.** `tools/templates/slide-review.html` *is* the review page
— its embedded JavaScript does all the rendering. `mpk review build` only
substitutes the data block. So there is a single implementation, shared by the
tool and by the prompt, and no third description to drift.

Templates live in `tools/templates/` because later layers need their own:
Layer 4 a transcript table, Layer 6 a vocabulary swatch sheet, Layer 8 the
sequence player. Each is a template filled with data — never a new renderer.

```
mpk review templates                     # what is available
mpk review build m.json -o out.html      # default: slide-review
mpk review build m.json -t slide-review -o out.html
```

### Required — frozen

| Field | Read by | Why it cannot be omitted |
|---|---|---|
| `element_id` | 5, 8 | Every later binding names it; must be stable |
| `tag` | 8 | Decides what gets a reveal beat |
| `semantic_type` (or `null`) | 5 | `null` is the signal that resolution is needed |
| `semantic_type_prior` | 5 | The evidence Layer 5 weighs against the narration |
| `endpoints` + `direction_verified` | 5, 8 | Which nodes an edge joins, and whether that is known |
| `properties.text` | 5, 8 | Matching narration to elements |
| `properties.lines[]` | 8 | One reveal per line a viewer sees; `paragraphs[]` merges soft-broken lines |
| `flags[]` | 5; review page | Carries what needs a human look |
| `deck.entity_inventory` | **6** | The topic vocabulary is built from it |
| `deck.chrome_pattern` | 5 | What not to re-lay-out per slide |

### Observed — open

`shape_kind`, raw fills and line colours, `paragraphs[]`, `ooxml_name`,
`rotation`, table grids, `speaker_notes`, `id_coverage`. Append freely;
promote to Required only when a later layer actually reads it.

### Settled schema questions

| # | Question | Decision |
|---|---|---|
| 1 | Flat list or nested tree | **Flat, with `parent_id`** for group members |
| 2 | Stable element ids | `<slide_id>_<ooxml_shape_id>`. Stable across re-runs of the same file; **changes if the deck is re-authored** — a stated limitation, not a hidden one |
| 3 | Colour-as-prior field shape | `semantic_type_prior: {value, basis, confidence}` |
| 4 | `realizes` — this layer or later | Recorded here as `realizes_prior` / `labels_prior`; **confirmed by Layer 5** |
| 5 | Units | Native EMU, stated in metadata, never converted |
| 6 | Scope | Per deck, one manifest per video |

---

## 4 · Review before proceeding

| # | Check |
|---|---|
| 1 | Does the slide count match the deck? |
| 2 | Is every `element_id` derived from the OOXML shape id — none sequential by reading order? |
| 3 | Re-run step 1: do all element ids come out identical? |
| 4 | Are id gaps reported per slide, with a reading of why? |
| 5 | Were tables (`graphicFrame`) captured, not silently skipped? |
| 6 | Were groups descended into, with `parent_id` set and transforms resolved? |
| 7 | Does any `semantic_type` carry a value that actually needed narration to decide? |
| 8 | Is every connector's direction either evidenced or flagged unverified? |
| 9 | Is notation verbatim — subscripts, braces and operators intact (VGR-01)? |
| 10 | Is chrome classified once and referenced, not re-derived per slide? |
| 11 | Is the same recurring element tagged the same way on every slide it appears on? |
| 12 | Does `entity_inventory` contain everything Layer 6 will need to build a vocabulary from? |
| 13 | Does everything needing a human look appear in `flags[]` rather than only in prose? |
| 14 | Could someone approve a slide from the review page alone? |
| 15 | Does the review page open and render? A blank page means the embedded JSON is malformed |
| 16 | Is the embedded manifest identical to output 1 — not a summary of it? |
| 17 | Does every text asset carry `lines[]`, and does its count match what a viewer sees? |
| 18 | Did `mpk deck extract --expect N` agree with the deck? |

Check 3 is the one to actually perform rather than reason about. A stable-ID
scheme that turns out not to be stable invalidates every artifact built on it,
and discovering that at Layer 8 costs every beat sheet written by then.

### What the next layers need

| Layer | Needs |
|---|---|
| **5** Representation | Context-dependent identities left `null` with priors; ids that still mean the same thing; `properties.text` verbatim; `chrome_pattern` so it does not re-lay-out furniture |
| **6** Vocabulary | `deck.entity_inventory` — the whole reason this layer is deck-scoped |
| **4** Transcript | **Nothing.** Runs in parallel, shares no inputs |

---

## Verification run — V017 slide 2

First run, one slide, fresh chat. **One round.** What it demonstrated:

| Result | Detail |
|---|---|
| ✅ Hardest field evidenced | Both connectors resolved via `a:stCxn`/`a:endCxn` + `a:tailEnd`; `_15`'s `rot="10800000" flipH="1"` was worked through to confirm the arrowhead lands at Consumer-left |
| ✅ Boundary rule held | All five chrome elements got a `semantic_type`; every diagram element left `null` with a prior. No leakage |
| ✅ Refused a false convention | `colour_convention_prior: "not_applicable"` — line colour `EEECE1` is neither red nor green. The red/green convention belongs to the deadlock decks, not this one |
| ✅ Honest about limits | Background raster and logo flagged `raster_content_unread`; the `flowChartPredefinedProcess` shape flagged for eye-check |
| ⚠ Found: notes not in data | The review table carried observations absent from the JSON → **`flags[]` added in v3** |
| ⚠ Found: id gaps invisible | Ids ran 3,4,5,6,9–12,14–16,20; the gaps at 13 and 17–19 went unreported → **`id_coverage` added in v3** |
| ⚠ Found: label orphaned | "BUFSIZE" sits above the buffer with nothing expressing the relationship → **`labels_prior` added in v3** |
| ⚠ Untested | Tables, groups, multi-slide consistency — none present on slide 2 |

---

## Changelog

- **v4** — step 1 now points at `mpk deck extract` rather than an inline script,
  and step 3 has two paths: **3A** `mpk review build` (default) or **3B** the
  prompt fills the template. Added `lines[]` as a Required field with its own
  prompt section — PowerPoint's `<a:br/>` soft breaks mean `paragraphs[]`
  silently merges lines a viewer sees separately, which would collapse three
  code-line reveals into one. Confirmed on the V017 deck: 8 visual lines across
  6 paragraphs in both code blocks. Review pages moved to
  `tools/templates/`, with `slide-review.html` the single owner of Layer 3's
  page; the standalone renderer was removed. Later layers add their own
  templates there rather than new renderers.

- **v3.1** — the review page is now produced **by the prompt**, not by running
  a script. The slide-review template is attached as an input; the prompt emits
  it verbatim with the manifest substituted into its embedded
  `<script type="application/json">` block, and the page renders itself in the
  browser. The view-of guarantee gets *stronger*, not weaker: the table and the
  data are now literally the same object in one file. `manifest_to_html.py` is
  kept as a batch utility for regenerating pages outside a chat.

- **v3** — deck scope (one `.pptx` → one manifest). Added the deck-level block:
  `chrome_pattern`, `entity_inventory` (Layer 6's input, which nothing produced
  before), `colour_convention`, `slide_index`, `speaker_notes`, `id_coverage`,
  `consistency`. Added `flags[]` as a real field, `labels_prior`, table and
  group handling, native-EMU units, and a slide-count assertion. Review page
  moved to a generator so it cannot drift. All prompted by the V017 s02 run.

- **v2** — restructured around the two-form rule; review table became the
  primary output; extraction script downgraded to optional.

- **v1** — written before first run.
