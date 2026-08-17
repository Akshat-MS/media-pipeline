# Layer 1 — Global Style Contract: Token Schema & Prompt

Companion to `docs/workflow/playbook.md`. Purpose: make Layer 1 produce
consistent, concrete output instead of vague prose.

---

## The governing principle

**Layer 1 is a stylesheet, not a template.**

| Question | Answered by |
|---|---|
| What does an H2 look like? | **Layer 1** |
| Does this slide have an H2? | Layer 3 |
| Where does the H2 sit on this slide? | Layer 3 |
| What does a "process" node look like? | Layer 4 |

Define every element type **unconditionally**, with no reference to any
particular slide. "Is this on every slide?" is not a Layer 1 question.

**Two categories inside Layer 1:**

| Category | What it is | Position owned by |
|---|---|---|
| **Chrome** | Canvas-level furniture — background, footer band, safe margins, grid | **Layer 1** (fixed, identical every slide) |
| **Type styles** | Definitions for H1/H2/body/bullets/code/etc. | Layer 3 (per slide) |

Chrome owns its own position because it is canvas, not content.

---

## Why previous attempts returned vague output

| Cause | Fix |
|---|---|
| Aesthetic judgment + concrete specs requested together | Split into two steps: choose direction, then fill tokens |
| No fixed key set — model invents a new structure each run | Provide the key list; **model fills values only, may not add/rename/omit keys** |
| Sizes picked arbitrarily | Require a **modular scale** (base × ratio) so sizes are derived |
| No specimen | Require a **specimen slide** rendering every token in use |

---

## The token schema

Fixed keys. Every one must be filled or explicitly marked `null` with a reason.

### 1 · Canvas & grid

| Token | Value | Notes |
|---|---|---|
| `canvas.width` | 1920 | TGT-001 |
| `canvas.height` | 1080 | TGT-001 |
| `canvas.fps` | 30 | TGT-002 |
| `grid.columns` | | 12 is conventional |
| `grid.gutter_px` | | |
| `safe_margin.top_px` | | |
| `safe_margin.right_px` | | |
| `safe_margin.bottom_px` | | must clear the footer band |
| `safe_margin.left_px` | | |
| `spacing.base_unit_px` | | all spacing is a multiple of this |

### 2 · Background (chrome)

| Token | Value | Notes |
|---|---|---|
| `background.type` | | `solid` \| `gradient` \| `textured` |
| `background.base_color` | | hex |
| `background.gradient.from` | | null if solid |
| `background.gradient.to` | | null if solid |
| `background.gradient.angle_deg` | | null if solid |
| `background.texture_ref` | | null if none |
| `background.contrast_ratio_vs_body_text` | | **must be ≥ 7:1** for projector legibility |

### 3 · Footer (chrome)

| Token | Value | Notes |
|---|---|---|
| `footer.height_px` | | |
| `footer.background` | | may differ from slide background |
| `footer.content_slots` | | e.g. `["attribution", "logo", "slide_number"]` |
| `footer.text_style_ref` | | points at a type style below |
| `footer.divider` | | style of the separating line, or null |

### 4 · Palette — roles, NOT entity assignments

| Role | Colour | Meaning | Contrast vs background |
|---|---|---|---|
| `neutral_structure` | | inert scaffolding | |
| `focus_attention` | | what to look at now | |
| `state_a` | | *(role meaning assigned per topic in Layer 4)* | |
| `state_b` | | | |
| `state_c` | | | |
| `warning_error` | | | |

Roles are named and coloured here. **Which entity claims which role is
Layer 4.** Named `state_a/b/c` rather than `blocked_waiting` etc. because the
five videos cover different mechanics — semantics get bound per topic.

### 5 · Type scale

Do not pick sizes freely. Declare a scale and derive from it.

| Token | Value |
|---|---|
| `type_scale.base_px` | |
| `type_scale.ratio` | e.g. 1.25 (major third) |
| `type_scale.steps` | how many steps above/below base |

### 6 · Type styles

Every row filled. Size expressed as a **scale step**, with the resolved px.

| Style | Family | Weight | Scale step | Size px | Colour role | Line height | Letter spacing | Notes |
|---|---|---|---|---|---|---|---|---|
| `h1` | | | +3 | | | | | slide title |
| `h2` | | | +2 | | | | | section |
| `h3` | | | +1 | | | | | sub-section |
| `body` | | | 0 | | | | | base |
| `body_emphasis` | | | 0 | | | | | inline emphasis |
| `caption` | | | −1 | | | | | small annotation |
| `label` | | | −1 | | | | | diagram labels |
| `code` | | | −1 | | | | | **monospace** — pseudocode |
| `math` | | | 0 | | | | | formal notation (VGR-01) |
| `table_header` | | | −1 | | | | | matrices |
| `table_cell` | | | −1 | | | | | matrices |
| `footer_text` | | | −2 | | | | | |

**`code`, `math`, `table_*` are not optional.** V029 (Banker's Algorithm Data
Structures) is matrices; V030 (Safety Algorithm) is pseudocode. VGR-01
requires formal notation survive verbatim — it needs a style to survive *into*.

### 7 · Lists & bullets

Per level. Levels 1–3 minimum.

| Level | Marker shape | Marker size px | Marker colour role | Indent px | Gap to text px | Text style ref | Vertical gap px |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | `body` | |
| 2 | | | | | | `body` | |
| 3 | | | | | | `caption` | |

### 8 · Tables (matrices)

| Token | Value |
|---|---|
| `table.border_style` | |
| `table.border_colour_role` | |
| `table.cell_padding_px` | |
| `table.header_fill` | |
| `table.zebra_striping` | true/false |
| `table.alignment_numeric` | usually `right` |

### 9 · Animation defaults

| Token | Value | Notes |
|---|---|---|
| `reveal.default_duration_s` | | |
| `reveal.easing` | | |
| `reveal.stagger_s` | | between sibling items |
| `camera.default_duration_s` | | |
| `camera.easing` | | |
| `state_motion.default_duration_s` | | |
| `slide_transition.type` | | between slides |
| `slide_transition.duration_s` | | |
| `layering.rule` | dimensions compose, not either/or | VGR-02 |

---

## The rewritten prompt

### Step 1 — choose a direction (aesthetic judgment only)

> **Inputs:** `shared/requirements/layer0-requirements.md`. Use only: VGR-02, VGR-03,
> TGT-001…004.
>
> Propose **3–4 theme directions** for an educational animation series — five
> Operating Systems lecture videos sharing one visual identity. Themes are
> chosen for **student engagement and legibility on a projector**, not derived
> from the customer's existing decks (those are content only).
> Cover a genuine range: at least one dark, one light, one alternative.
>
> **Render each as a specimen slide**, 16:9 at 1920×1080 proportions. Each
> specimen must show, on one slide: an H1 title, an H2, three body bullets at
> levels 1–3, one line of monospace pseudocode, a small 3×3 numeric matrix,
> a diagram area with **neutral unlabeled geometry** (plain nodes and
> connectors), and the footer band.
> Placeholder geometry is deliberate — entity vocabulary is Layer 4. Judge
> these on background, palette contrast, typography legibility, and tone only.
>
> For each direction give: a 2–3 sentence rationale; the palette with the
> **role** each colour serves (not which entity uses it); the typography
> pairing and why it is legible at 1080p; and the trade-offs.
>
> Do not assign colours to diagram entities. Do not define shapes or icons.
> Do not produce JSON or token tables yet.

**Why a specimen slide:** typography cannot be judged from a size list. One
slide exercising every token exposes problems a description hides — H2 too
close to H1, code font clashing, matrix unreadable at that size.

### Step 2 — fill the tokens (no aesthetic judgment)

> Here is the approved theme direction. Fill the token schema below.
>
> Rules:
> - Fill **values only**. Do not add, rename, reorder, or omit keys.
> - Every token gets a value, or `null` **with a one-line reason**.
> - Type sizes derive from the declared modular scale — state the step and
>   the resolved px. Do not pick sizes independently.
> - All spacing is a multiple of `spacing.base_unit_px`.
> - Colours reference palette **roles**, never raw hex, outside the palette
>   block itself.
> - State the measured contrast ratio for body text on background; it must be
>   ≥ 7:1.
> - Do not include entity grammar — no shapes, icons, or entity→colour
>   assignments. If something appears to need one, list it as an open question
>   for Layer 4.
>
> [paste token schema]

### Step 3 — verify before approving

> Render the specimen slide again using the **filled tokens** (not the step-1
> visual), and list any token whose value looks wrong at full scale.

**Review the specimen full-screen, not in a preview pane.** A sample viewed
small reads as legible even when the body size would fail on a projector.

---

## Why this produces better output

| Problem | Mechanism that fixes it |
|---|---|
| Vague prose | Step 2 has no aesthetic latitude — it is a fill task |
| Inconsistent structure between runs | Fixed key set, explicitly forbidden to change |
| Arbitrary sizes | Derived from a declared modular scale |
| Missing values | "Every token or `null` with a reason" — silence is not allowed |
| Can't judge the result | Specimen slide exercising every token |
| Layer bleed | Explicit instruction to defer entity questions to Layer 4 |

---

## Open items

- **Palette role count.** Six roles is a starting guess. The right number
  depends on how many simultaneous states the OS topics need to distinguish —
  worth checking against the busiest slide across all five decks before
  locking.
- **Slide transitions** sit in Layer 1 as an animation default, but arguably
  belong to sequencing. Left here for now since they are global and content-
  independent; revisit if per-slide variation turns out to be wanted.
