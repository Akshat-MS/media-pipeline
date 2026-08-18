# Layer 2 — Global Theme

**Scope:** once, all five videos · **Prompt version:** v2 · **Work status:** complete (contract v3)
**Emits:** `style-contract.md` + `global_style_contract.json` + reference specimens

> **Supersedes** `docs/workflow/layer-captures/layer1-token-schema-and-prompt.md`
> (old numbering: theme was Layer 1). That document's token-schema technique,
> its chrome/type-style distinction, and its round-trip verification step are
> merged in below. It is retained as provenance — it is the record of how this
> prompt was first repaired.
>
> **Note on this prompt.** Layer 2's *work* was completed before this playbook
> existed. The prompt originally used asked only for background, palette,
> typography and animation defaults — it did **not** ask for the grid, the type
> scale, the separate `math` style, the measured contrast table, or the
> colour-blindness channel assignment. All five arrived through three rounds of
> iteration (contract v1 → v2 → v3).
>
> Per prompt-quality rule 8, **the amended prompt is the artifact worth
> keeping**, not the output. The prompt below is written from the delivered
> contract, so a re-run reaches v3 in one pass rather than three.

---

## 1 · What it does

Selects the **visual system** shared by all five videos: canvas and grid,
type scale and type styles, background, palette roles, chrome (lists, tables,
code blocks, footer), and animation defaults.

**The decision this layer owns:** what an element *looks like*, unconditionally.

**Layer 2 is a stylesheet, not a template.**

| Question | Answered by |
|---|---|
| What does a heading level 2 look like? | **Layer 2** |
| Does this slide have one, and where? | Layer 5 |
| What does a "process" node look like? | Layer 6 |
| What colour is a request edge? | Layer 6 — it *claims a role* defined here |

Every element type is defined **unconditionally**, with no reference to any
particular slide. *"Is this on every slide?"* is not a Layer 2 question.

### Two categories inside Layer 2 — they differ on who owns position

| Category | What it is | Position owned by |
|---|---|---|
| **Chrome** | Canvas-level furniture — background, footer band, safe margins, grid | **Layer 2.** Fixed, identical on every slide |
| **Type styles** | Definitions for h1 / h2 / body / bullets / code / math | **Layer 5**, per slide |

Chrome owns its own position because it is *canvas*, not *content*. A type
style says what a heading looks like; it cannot say where the heading goes,
because that depends on the slide.

### What is deliberately excluded

**Layer 2 contains no entity grammar.** No shapes, no icons, no entity→colour
assignments. Process/resource/edge vocabulary is deadlock-specific;
producer/consumer/buffer is bounded-buffer-specific. Those are per-topic and
belong to Layer 6.

**Palette roles are named but unassigned.** A colour is defined as *meaning*
something; which entity claims that meaning is decided per topic. This is what
keeps colour meaning identical across all five videos while letting the
vocabulary differ.

**The theme is a fresh design choice for engagement** — deliberately not derived
from the customer's decks. Those are content, not a style reference. Deriving
the theme from them would reproduce the flat original.

---

## 2 · The prompt to run

**Four steps. Do not collapse them.** Each is a different kind of work, and
mixing two of them is what produced vague output on the first attempts.

| Step | Kind of work | Why separate |
|---|---|---|
| 1 | Aesthetic judgement | A theme cannot be judged from a written description |
| 2 | Measurement | This is where every real improvement came from |
| 3 | Transcription — **no judgement at all** | A fill task has no room to be vague |
| 4 | Round-trip check | Proves the tokens actually reproduce the visual |

### Why the earlier attempts returned vague output

| Cause | Mechanism that fixes it |
|---|---|
| Aesthetic judgement and concrete specs requested together | Split: step 1 chooses, step 3 fills |
| No fixed key set — a new structure invented each run | Supply the keys; values only, no adding or renaming |
| Sizes picked arbitrarily | Require a modular scale so sizes are *derived* |
| Missing values indistinguishable from deliberate omissions | Every token, or `null` with a reason |
| No way to judge the result | A specimen exercising every token |
| Layer bleed into entity vocabulary | Explicit instruction to defer to Layer 6 |
| **Nothing verified** | **Step 2 — added after contract v3; see below** |

Step 2 is the newest addition. Every significant improvement between contract
v1 and v3 — the green base darkened for contrast headroom, footer opacity
raised from 3.84:1 to 5.3:1, the amber/red collision under colour blindness,
the tan accent replaced — came from measuring, not from designing. Asking for
it explicitly converts three rounds into one.

---

### Step 1 — choose a direction (aesthetic judgement only)

```
INPUTS: the Layer 1 registers (delivery-targets.md, visual-grammar.md).
Use only: VGR-02, VGR-03, TGT-001, TGT-002. Ignore all other entries.
If a requirement outside that list appears relevant, name it and stop —
do not act on it.

Propose 3-4 theme directions for an educational animation series: five
Operating Systems videos sharing one visual identity.

Themes are chosen for STUDENT ENGAGEMENT AND LEGIBILITY ON A PROJECTOR.
They are NOT derived from the customer's existing decks — those are content,
not a style reference, and deriving from them would reproduce the flat
original we are replacing. Cover a genuine range: at least one dark, one
light, and one alternative direction.

RENDER EACH AS A WORKING HTML SPECIMEN at 1920x1080, using real fonts (not
fallbacks — a specimen in fallback fonts tests the wrong thing).

Each specimen must show every element type the five videos actually need,
because a theme that looks good on a title slide can fail on a matrix:

  - eyebrow, title, heading level 2, heading level 3
  - bullet list at THREE indent levels
  - mathematical notation with true subscripts and italic variables
    (e.g. P = {P1, P2, ... Pn} and Pi -> Rj and Needi <= Work)
  - a small numeric matrix table
  - a code block with a keyword and a comment
  - a legend showing every palette role
  - the footer band with attribution and slide number

For the palette legend use NEUTRAL UNLABELLED GEOMETRY — plain lines and
nodes. Do NOT draw processes, resources, or any named entity. Entity
vocabulary is Layer 6, and putting it here would bind a colour to a meaning
before the per-topic decision has been made.

For each direction give, IN THIS ORDER:
  1. the rationale (2-3 sentences) — reasoning first
  2. the palette, WITH A SEMANTIC ROLE NAMED PER COLOUR
  3. the typography pairing and why it is legible at 1080p
  4. the trade-offs

ON NAMING PALETTE ROLES — this is the part that most easily goes wrong.
A role name must state WHAT THE COLOUR MEANS, so that the meaning stays
identical across all five videos. "blocked_waiting", "granted_active",
"focus_attention" are correct. "state_a", "colour_1", "primary" are NOT
acceptable: they satisfy the instruction while carrying no meaning, and
nothing then prevents the same colour meaning "blocked" in one video and
"granted" in another. If you cannot say what a colour means, it is not a
role and should not be in the palette.

ALSO STATE how many distinct roles the material actually needs, judged from
the busiest slide across the five decks — not from a round number. Every
role beyond what is needed costs contrast headroom and colour-vision
separation.

DO NOT assign colours to diagram entities. DO NOT define shapes or icons.
DO NOT produce JSON or token tables yet — that is step 3.

End with:
UNRESOLVED / ASSUMPTIONS / FLAGS
```

**Review the specimens at true scale before continuing.** A sample viewed
small in a chat window reads as legible when the body size would fail on a
projector. TGT-001 implies real pixel sizes that only matter full-screen.

---

### Step 2 — measure and verify the chosen direction

```
INPUTS: the approved specimen from step 1.

Verify it. Report measurements, not impressions. Every number here becomes
part of the contract, so a number you estimated will be cited as if it were
measured.

1. CONTRAST — measure the ratio of every text and palette token against its
   actual background. One row per token. State the WCAG AA floor (4.5:1) and
   our stricter target (7:1), and mark which values sit between them.

2. BACKGROUND UNIFORMITY — if a background is a gradient, contrast varies by
   position on the canvas. Measure at the extremes. A token that passes at
   one corner and fails at another is a defect, not a trade-off.

3. COLOUR VISION — simulate deuteranopia, protanopia and tritanopia across
   the full palette. Report which role pairs become indistinguishable, with
   the simulated separation ratio.

   Where two roles collide, DO NOT simply drop one. Assign each role a
   SECOND, NON-COLOUR CHANNEL, because colour must never carry meaning
   alone — this keeps diagrams readable in greyscale, on a poor projector,
   and under any colour deficiency, and it satisfies VGR-02 (dimensions
   compose) rather than fighting it.

   THE SECOND CHANNEL MUST BE DEFINED PER SHAPE CLASS. A line style
   (dashed / solid / dotted) works for a connector but does not exist on a
   filled node. Give each role a channel for: connectors, filled shapes,
   and text/labels. A role whose only channel is line style is undefined
   for two thirds of the diagram.

4. If a replacement hue would resolve a collision, search for one and report
   the search: which hue families were tried, the best separation achieved,
   and whether any hue meets all constraints. If none does, say so and state
   which channel carries the distinction instead.

5. FULL-SCREEN LEGIBILITY — confirm on a real 1080p display, not a preview
   pane. Report the smallest type size used and whether it holds.

6. GRID ARITHMETIC — show that columns and rows reconcile to the available
   space, including any clearance reserved for chrome. State the
   reconciliation explicitly; a bare "= 888" that does not match the
   available height reads as an error even when it is correct.

Values that cannot be measured stay null. Do not guess.

End with:
UNRESOLVED / ASSUMPTIONS / FLAGS
```

---

### Step 3 — fill the token schema (no aesthetic judgement)

```
INPUTS: the approved direction, the step 2 measurements, and the token
schema below.

Fill the schema.

RULES:
- Fill VALUES ONLY. Do not add, rename, reorder, or omit keys. A new
  structure every run makes two contracts impossible to diff, and makes the
  renderer's job unknowable.
- Every token gets a value, or `null` WITH A ONE-LINE REASON. Silence is not
  allowed: a key quietly left out reads as "not applicable" when it usually
  means "not considered".
- Type sizes DERIVE from the declared modular scale — state the step and the
  resolved pixel value. Do not pick sizes independently.
- All spacing is a multiple of `spacing.base_unit_px`.
- Outside the palette block itself, colours reference palette ROLES, never
  raw hex.
- Carry the measured contrast ratios through from step 2. Do not re-estimate.
- Every entry carries a `satisfies` field citing a VGR or TGT id, or a
  one-line rationale.
- DO NOT include entity grammar — no shapes, icons, or entity→colour
  assignments. If something appears to need one, list it as an open question
  for Layer 6.

THE KEY SET:

  canvas             width, height, fps, safe_margin{top,right,bottom,left},
                     spacing_base_unit_px
  grid               columns, column_width_px, rows, row_height_px, gutter_px,
                     content_area, col_origin_fn, row_origin_fn, span_fn
  type_scale         base_px, ratio
  themes[]           per variant: background{base_color, accents[]},
                     text_secondary, text_tertiary, eyebrow, accent_marker,
                     measured_body_contrast
  theme_for_series   which variant these five videos ship with
  palette_roles      per role: semantic name, colour, measured contrast, and
                     channels{connector, filled_shape, label}
  type_styles        per style: family, weight, step, size_px, line_height,
                     colour_role, tracking, transform
  lists              per level: marker, size, indent, gap, text_style
  table              border, cell_padding, header_fill, rowhead_fill,
                     zebra_striping, alignment_numeric
  code_block         background, border_left, border_left_role, padding, radius
  footer             layout, baseline_px, rule, rule_offset_px, slots, colour
  animation_defaults per dimension: default_s, floor_s, compression_rule,
                     easing, variants, usage_rule, satisfies
  pacing             binding, fixed_sleeps_allowed, min_gap_between_actions_s,
                     dead_air_defect_threshold_s
  output_encode      citing TGT ids, never repeating the numbers
  required_fonts     list
  verification       contrast_measured, colourblind_checked,
                     legibility_verified_fullscreen
  version            payload version — must match the document version
  schema_version     bump when the key set changes; register a migration

ON ANIMATION DURATIONS — express every duration as a DEFAULT WITH A FLOOR
AND A COMPRESSION RULE, never as a fixed constant. A fixed duration is a
fixed sleep wearing a different name: if the narration phrase takes 1.27s
and the contract says 1.1s, the motion desynchronises from the words.
Layer 8 measures the real duration from the narration and needs to know how
far it may compress, and what to do when the phrase is shorter than the
floor. State: default, floor, and the under-run policy.

ON GROUPING — chrome (background, footer, safe margins, grid) owns its own
position because it is canvas. Type styles do not carry position; Layer 5
places them.

ON VERSIONING — the payload version, the document version and the
schema_version must agree. Where the key set changes, bump schema_version
and register a migration; do not overwrite.

End with:
UNRESOLVED / ASSUMPTIONS / FLAGS
```

---

### Step 4 — re-render from the filled tokens

```
INPUTS: the filled token schema from step 3.

Rebuild the specimen using ONLY the filled tokens — not the step 1 visual.
Then list every token whose value looks wrong at full scale.

This closes the loop. A token set that cannot reproduce the approved
specimen is not a description of it, and the renderer will inherit that gap.

Review the result full-screen, not in a preview pane.
```

---

## 3 · What it emits

### Required — frozen

| Field group | Why Layer 5, 6 or 8 cannot run without it |
|---|---|
| `canvas` + `grid` | Layer 5 selects cells; Layer 8 positions camera moves |
| `palette_roles` with **semantic names** and per-shape-class channels | Layer 6 binds entities to roles |
| `type_styles` | Layer 5 assigns styles to content |
| `animation_defaults` with **floor and compression rule** | Layer 8 derives real durations |
| `pacing` | Layer 8's binding mode and dead-air threshold |
| `output_encode` citing TGT ids | Render and validation |

### Observed — open, append freely

Contrast measurements, colour-vision simulation results, the rejected-hue
search, theme-specific text tokens, rationale prose, changelog.

### Artifacts produced

| Artifact | Path | Consumed by |
|---|---|---|
| Contract document | `docs/shared/specs/style-contract.md` | humans; Layers 5, 6, 8 |
| Contract runtime | `res/config/style/global_style_contract.json` | renderer; Layers 6, 8 |
| Reference specimens | `docs/shared/specimen/specimen-{navy,blue,green}.html` | visual reference; render check |
| Theme comparison | `docs/shared/specimen/compare-themes.html` | the selection decision |
| Gap specimens | `docs/shared/specimen/issues-specimen/` | evidence for each defect found |
| Bundled fonts | `docs/shared/specimen/fonts/*.ttf` | render host |

The specimen is the canonical implementation of the contract — if the two
disagree, one of them is wrong, and that is a defect rather than a difference
of opinion.

---

## 4 · Review before proceeding

| # | Check | Result on contract v3 |
|---|---|---|
| 1 | Does every palette role name state what it **means**? | ❌ **Fails** — `state_a` / `state_b` / `state_c` carry no meaning (OBS-005) |
| 2 | Does every role have a second channel for **every shape class**? | ❌ **Fails** — line style is defined, which does not exist on filled nodes (OBS-009) |
| 3 | Are animation durations expressed with a floor and compression rule? | ❌ **Fails** — fixed constants 0.3 / 0.8 / 1.1 s (OBS-008, OBS-022) |
| 4 | Is the pacing block present? | ❌ **Fails** — dropped between versions (OBS-007) |
| 5 | Do document version, payload version and schema_version agree? | ❌ **Fails** — doc v3, payload v1, schema_version 1.0.0 (OBS-006, OBS-014) |
| 6 | Is the number of palette roles justified by the material? | ❌ **Open** — six roles was a starting guess, never checked against the busiest slide (OBS-023) |
| 7 | Is contrast measured rather than estimated? | ✅ **Passes** — measured across all three themes |
| 8 | Is colour vision checked, with collisions resolved? | ✅ **Passes** — deuteranopia collision found; replacement-hue search run and documented |
| 9 | Is full-screen legibility verified on a real display? | ✅ **Passes** |
| 10 | Does the grid arithmetic reconcile to available space? | ✅ **Passes, but unstated** — see below |
| 11 | Is entity grammar absent? | ✅ **Passes** |

### Grid arithmetic — reconciled

The contract asserts `8 × 90 + 7 × 24 = 888` without showing how 888 relates to
the 932 px between the top and bottom margins. It does reconcile:

| | px |
|---|---|
| Available height (1080 − 96 top − 52 bottom) | 932 |
| Grid (8 rows × 90 + 7 gutters × 24) | 888 |
| Clearance from grid bottom to the footer rule | 22 |
| Footer rule to footer baseline | 22 |
| **Total** | **932 ✓** |

Verified against `specimen-blue.html`: the grid ends at y=984, the footer rule
sits at y=1006, the footer baseline at y=1028. **OBS-012 is documentation-only**
— state the reconciliation in the contract; nothing needs to change.

### What Layer 3 needs from this layer

Nothing. Layer 3 (asset deconstruction) reads only VGR-01 and the source slides;
it is independent of the theme. **None of the failures above block Layer 3 or
Layer 4** — they block Layer 6, which binds entities to palette roles, and
Layer 8, which needs the pacing and duration rules.

---

## Changelog

- **v2** — merged in `layer-captures/layer1-token-schema-and-prompt.md`, which
  had independently reached a multi-step structure. Absorbed: the **fixed key
  set** (fill values only, never restructure) and the explicit key list; **no
  silent omission** (every token or `null` with a reason); the **chrome vs type
  styles** distinction on who owns position; and a fourth step that
  **re-renders the specimen from the filled tokens** to prove they reproduce
  the approved visual. Added the palette-role-count question (OBS-023). Step
  ordering is now judge → measure → fill → verify.

- **v1** — prompt written from the delivered contract (v3). Split into steps;
  the measurement step was new — every improvement between contract v1 and v3
  came from measuring, and the original prompt never asked for it. Added: the
  semantic-role-naming rule with its reason and a worked counter-example
  (OBS-005); per-shape-class second channels (OBS-009); durations as
  default-plus-floor-plus-compression rather than constants (OBS-008, OBS-022);
  the pacing block (OBS-007); version agreement (OBS-006); explicit grid
  reconciliation (OBS-012); and the full element list a specimen must show.
