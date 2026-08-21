# Layer 2 — Global Style Contract · Token Table

**Artifact:** `global_style_contract` · **Version:** v3 (approved)
**Runtime file:** `config/style/global_style_contract.json` — generated from §12 of this document
**Scope:** global, all 5 videos (V017, V018, V028, V029, V030)
**Source:** `specimen_navy_v1.html`, `specimen_blue_v1.html`, `specimen_green_dark_v1.html`

---

## Governing principle

**Layer 1 is a stylesheet, not a template.**

| Question | Answered by |
|---|---|
| What does an H2 look like? | **Layer 1 (this document)** |
| Does this slide have an H2, and where? | Layer 3 |
| What does a "process" node look like? | Layer 4 |
| What colour is a request edge? | Layer 4 (it *claims a role* defined here) |

Every element type is defined **unconditionally**, with no reference to any
particular slide. This document contains **no entity grammar**.

---

## 1 · Canvas & grid

| Token | Value | Note |
|---|---|---|
| `canvas.width` | 1920 | TGT-001 |
| `canvas.height` | 1080 | TGT-001 |
| `canvas.fps` | 30 | TGT-002 |
| `safe_margin.left_px` | 120 | |
| `safe_margin.right_px` | 120 | |
| `safe_margin.top_px` | 96 | eyebrow baseline |
| `safe_margin.bottom_px` | 52 | footer baseline |
| `spacing.base_unit_px` | 4 | all spacing is a multiple |
| `grid.columns` | 12 | |
| `grid.column_width_px` | 118 | 12×118 + 11×24 = 1680 ✓ |
| `grid.rows` | 8 | |
| `grid.row_height_px` | 90 | 8×90 + 7×24 = 888 ✓ |
| `grid.gutter_px` | 24 | both axes |

**The grid replaces the previous fixed 2-column split.** It is an invisible
coordinate system, not a layout. Layer 3 still chooses the layout per slide —
column split, row split, full-bleed — but selects *grid cells* rather than
inventing pixel positions.

Without it, three consecutive slides with different layouts landed their left
edges at 36/48/30px and content tops at 70/64/80px — which reads as a visible
frame twitch on every slide change. With it, layouts vary freely while
alignment is inherited.

**Cell addressing:** `col(n) = 120 + (n-1) × 142` and
`row(n) = 96 + (n-1) × 114`, where 142 = 118 + 24 and 114 = 90 + 24.
A span of *k* columns is `k × 118 + (k-1) × 24`.

---

## 2 · Type scale

| Token | Value |
|---|---|
| `type_scale.base_px` | 31 |
| `type_scale.ratio` | 1.25 |

| Step | Computed | Used by |
|---|---|---|
| +3 | 60.5 → **60** | h1 |
| +2 | 48.4 → **48** | h2 |
| +1 | 38.8 → **39** | h3 |
| 0 | **31** | body, body_emphasis |
| −1 | 24.8 → **25** | caption, label, code, table |
| −2 | 19.8 → **20** | eyebrow, footer |

All sizes derived from the scale — none hand-picked.

---

## 3 · Theme variants — background

Three candidates, all **flat base + soft radial accents** (no gradient, no
frames, no corner chrome). One must be selected.

### A · Navy
```
background.base_color   #16234A
background.accent_1     radial circle at 12% 6%,  rgba(120,150,220,0.28) → transparent 22%
background.accent_2     radial circle at 78% 78%, rgba(90,120,200,0.30)  → transparent 30%
```

### B · Blue
```
background.base_color   #0B2E5C        (45% stop of gradient_unbounded, flattened)
background.accent_1     radial circle at 12% 6%,  rgba(110,165,240,0.26) → transparent 22%
background.accent_2     radial circle at 78% 78%, rgba(70,130,215,0.28)  → transparent 30%
```

### C · Military green (darkened)
```
background.base_color   #26301C        (darkened from #3B4A2C — see note)
background.accent_1     radial circle at 12% 6%,  rgba(150,180,115,0.22) → transparent 22%
background.accent_2     radial circle at 78% 78%, rgba(120,150,90,0.24)  → transparent 30%
```

**Why green was darkened:** the source `#3B4A2C` has luminance 0.060 — over
3× navy's 0.019. At that value `state_c` (4.13:1) and `warning` (3.44:1)
fell below WCAG AA, and the file's own tan accent `#D9A25E` measured 4.21:1.
Darkening to `#26301C` restores headroom without losing the olive character.

**All three are uniform.** None has the position-dependent contrast problem
of the original gradient (which swung 5.91 → 11.18:1 across the canvas).

---

## 4 · Palette — slots, not meanings

This section defines **slots**: colours verified to be distinguishable from one
another, each with a redundant non-colour channel (§8). A slot is a visual fact.
It carries no meaning.

**Binding a meaning to a slot is Layer 6's decision, not this document's.**
Nothing here says what amber means. `state_a`, `state_b`, `state_c` are
deliberately empty names and must stay that way — naming a slot `blocked_waiting`
would force a rename across every artifact the day a topic needs the slot for
something else.

### The binding rule — one direction only

> **The same meaning takes the same slot in every video.**
> The same slot may carry different meanings in different videos.

The rule runs one way on purpose. A viewer never watches two videos at once, so
a slot reused across topics costs nothing. A meaning that changes colour between
videos costs trust — it is the defect this rule exists to prevent.

Because it is one-way, **many meanings may share one slot.** The slots are not a
budget of three ideas; they are three distinguishable groups.

### When two meanings may share a slot

> **Two meanings may share a slot unless a viewer would ever need to tell them
> apart.**

| Example pair | Need to tell apart? | Verdict |
|---|---|---|
| code-block edge · request line | No — a panel border and an arrow between nodes are never compared | share one slot |
| error code · working code | **Yes** — that distinction *is* the teaching point | different slots |

Layer 6's binding table must list every meaning bound to each slot, so a
reviewer can read one table and ask that single question of each slot. A
binding that is not written down cannot be checked.

### Ownership

| | |
|---|---|
| **This document owns** | which slots exist, their colours, their measured contrast, their redundant channels |
| **Layer 6 owns** | which meaning takes which slot |
| **Scope of the binding** | **project-level, extended per topic, never contradicted.** "Blocked" appears in bounded buffer, reader-writer *and* Banker's. Per-topic binding files would each choose a slot independently and could disagree — breaking the one-way rule with the very artifact meant to enforce it. Shared meanings are decided once; a topic adds only what is unique to it |

| Role | Colour | Shared across themes? |
|---|---|---|
| `text_primary` | `#FFFFFF` | yes |
| `text_secondary` | per theme (see §5) | no |
| `text_tertiary` | per theme | no |
| `accent_marker` | per theme | no |
| `neutral_structure` | `rgba(255,255,255,0.22)` | yes |
| `state_a` | `#F2A33C` amber | yes |
| `state_b` | `#3FD0C9` cyan | yes |
| `state_c` | `#B79CF5` violet | yes |
| `focus_attention` | `#FFD84D` yellow | yes |
| `warning_error` | `#FF6B6B` red | yes — **see §8** |

State roles are theme-independent so semantic colour meaning stays identical
across all five videos regardless of which background is chosen.

---

## 4a · Bindings this contract makes, and why

Three tokens in this document bind a slot to a meaning. They were scattered
across §6 and §7 and read as styling rather than as the semantic commitments
they are. They are collected here so Layer 6 can see what is already taken.

| Token | Slot | Why it is here rather than in Layer 6 |
|---|---|---|
| `type_styles.code_keyword.colour_role` | `state_a` | A keyword is a keyword in every topic. Syntax colouring is typography, not subject matter |
| `type_styles.code_comment.colour_role` | `eyebrow` | Same reasoning. `eyebrow` is a text token, not one of the three slots |
| `code_block.border_left_role` | `state_b` | The edge marks *"this is code"* — a document-wide category, not a topic's idea |

**They are declared here, not moved.** Relocating them would change where the
loader reads them for no gain; the defect was that they were invisible, not that
they were in the wrong file.

**Note the interaction, because Layer 6 will meet it.** Inside a code block,
keywords are already `state_a`. If a topic binds `state_a` to something and
applies it to a code block's border, the result is amber keywords in an
amber-bordered box. Text and border are different visual categories, so a viewer
is unlikely to confuse them — but that judgement belongs to whoever writes the
binding table, and today nothing would surface it.

## 5 · Theme-specific text tokens

| Token | Navy | Blue | Green |
|---|---|---|---|
| `text_secondary` (body) | `#C6D0EC` | `#C6D6EE` | `#E3E7DE` |
| `text_tertiary` (level 3) | `#9FB0DA` | `#A3BCE4` | `#CBD2C4` |
| `eyebrow` / `panel_label` | `#8FA3D9` | `#8FB4E8` | `#EDC492` |
| `accent_marker` (bullets) | `#7C9BE8` | `#6FA6F0` | `#EDC492` |
| `footer` | `rgba(255,255,255,0.55)` | same | same |

---

## 6 · Type styles

| Style | Family | Weight | Step | Size | Colour role | Line height | Tracking |
|---|---|---|---|---|---|---|---|
| `eyebrow` | Space Grotesk | 500 | −2 | 20 | eyebrow | — | 0.1em, uppercase |
| `h1` | Space Grotesk | 600 | +3 | 60 | text_primary | 1.15 | — |
| `h2` | Space Grotesk | 600 | +2 | 48 | text_primary | 1.20 | — |
| `h3` | Space Grotesk | 500 | +1 | 39 | text_secondary | 1.25 | — |
| `body` | Inter | 400 | 0 | 31 | text_secondary | 1.50 | — |
| `body_emphasis` | Inter | 500 | 0 | 31 | text_primary | 1.50 | — |
| `caption` | Inter | 400 | −1 | 25 | text_tertiary | 1.40 | — |
| `label` | Inter | 500 | −1 | 25 | text_primary | — | — |
| `code` | **Space Mono** | 400 | −1 | 25 | text_secondary | 1.45 | — |
| `code_keyword` | Space Mono | 400 | −1 | 25 | `state_a` | 1.45 | — |
| `code_comment` | Space Mono | 400 | −1 | 25 | eyebrow | 1.45 | — |
| `math` | **Source Serif 4** | 400 | 0 | 31 | text_secondary | 1.40 | italic variables, true subscripts |
| `math_variable` | Source Serif 4 | 400 *italic* | 0 | 31 | text_secondary | 1.40 | — |
| `math_subscript` | Source Serif 4 | 400 *italic* | — | 0.62em | text_secondary | — | vertical-align −0.25em |
| `table_header` | Space Mono | 700 | −1 | 25 | text_primary | — | — |
| `table_cell` | Space Mono | 400 | −1 | 25 | text_secondary | — | — |
| `panel_label` | Space Grotesk | 500 | −2 | 20 | eyebrow | — | 0.08em, uppercase |
| `footer_text` | Space Grotesk | 400 | −2 | 20 | footer | — | — |

**Space Mono** chosen because it shares design DNA with Space Grotesk, so the
deck reads as one family rather than two bolted together.

**`code` and `math` are separate styles doing different jobs.** Monospace
exists for *alignment* — equal-width glyphs so matrix columns and code
indentation line up. It cannot render subscripts: every glyph is locked to the
same width and baseline, so `P1` reads as "P one" rather than "P sub one".
Since the decks use `Pᵢ`, `Rⱼ` and set notation like `P = {P₁, P₂, … Pₙ}`,
notation needs its own style. Serif italic is the standard convention for
mathematical variables and separates notation from both body text and code at
a glance.

| Job | Style | Example |
|---|---|---|
| Alignment (code, matrices) | `code` / `table_*` — Space Mono | `while Need[i] <= Work:` |
| Notation (variables, sets) | `math` — Source Serif 4 | *P*ᵢ → *R*ⱼ |

---

## 7 · Lists, tables, chrome

### Bullets

| Level | Marker | Size | Colour | Indent | Gap to text | Text style | Vertical gap |
|---|---|---|---|---|---|---|---|
| 1 | filled circle | 12px | accent_marker | 0 | 34px | `body` | 20px |
| 2 | hollow circle, 2px stroke | 10px | accent_marker | 44px | 34px | `body` | 20px |
| 3 | dash | 10×2px | accent_marker | 88px | 34px | `caption` | 20px |

### Tables (matrices)

| Token | Value |
|---|---|
| `table.border` | 1px `rgba(255,255,255,0.15)` |
| `table.cell_padding` | 12px 20px |
| `table.header_fill` | `rgba(255,255,255,0.06)` |
| `table.rowhead_fill` | `rgba(255,255,255,0.06)` |
| `table.zebra_striping` | false |
| `table.alignment_numeric` | right |

### Code block

| Token | Value |
|---|---|
| `code_block.background` | `rgba(255,255,255,0.04)` |
| `code_block.border_left` | 3px solid `state_b` — **a binding, see §4a** |
| `code_block.padding` | 20px 24px |
| `code_block.radius` | 3px |

### Footer

| Token | Value |
|---|---|
| `footer.layout` | flex, space-between, full content width |
| `footer.baseline` | 52px from bottom |
| `footer.rule` | 1px `rgba(255,255,255,0.12)`, 22px above baseline |
| `footer.slots` | **`["attribution", "brand_mark"]`** |
| `footer.contrast` | 5.58 / 5.12 / 5.30:1 on navy / blue / green |

Raised from the original 42% opacity (3.84:1, below AA) to 55%.

**Attribution** sits left: `©Ravi Subramanian`, in `footer.colour`.

**© is the copyright sign, not `@`.** Measured from the source video, where
`©Ravi Subramanian` appears bottom-left on every frame, including over the intro
and outro cards. Contract v5 read `@Ravi Subramanian`; `@` denotes a handle,
`©` denotes authorship. The source was right and the draft was a mis-hearing.

**The slide number was removed (v5).** Slide numbers exist for navigation, and a
video has none — a viewer cannot turn to slide 4. The token occupied a place on
every frame of every video and bought nothing.

This removes the number from the **screen only**. `slide_id` remains in every
internal artifact and is how Layer 8 binds a beat to an element; nothing
downstream is affected.

### Brand mark

Sits **right**, opposite the attribution. Specimen:
`docs/shared/specimen/footer-themes.html`, rendered on all three themes.

**A deliberate divergence from the source.** The original deck places the mark
**centred** in the footer band. This contract places it **right**. That choice was
made after reviewing the specimen full-screen, and is recorded so it reads as a
decision rather than an oversight.

| Token | Value |
|---|---|
| `brand_mark.src` | `res/library/icons/eklakshya-alpha.png` |
| `brand_mark.aspect_ratio` | 3.03 : 1 (497 × 164 after trimming) |
| `brand_mark.height` | **2.05% of frame width** ≈ 39px at 1080p |
| `brand_mark.plate.fill` | `#FFFFFF` |
| `brand_mark.plate.radius` | 4px |
| `brand_mark.plate.padding` | 0.5% × 0.8% of frame width |

Height and padding are expressed as a share of frame width, not pixels, so the
mark scales with the canvas. The plate sizes itself from the mark, so replacing
the asset with one of different proportions changes `aspect_ratio` and nothing
else.

#### Why a plate is required — measured, not assumed

| | on its own ground | navy `#16234A` | blue `#0B2E5C` | green `#26301C` |
|---|---|---|---|---|
| wordmark `#000327` | **18.81** | **1.32** | **1.50** | **1.46** |
| white plate | — | 15.29 | 13.47 | 13.80 |

The supplied mark is a dark wordmark. At 1.32:1 it is not merely hard to read on
navy — it is **invisible**. Every other token in this contract carries a measured
contrast figure; shipping the mark bare would have made it the one unmeasured
thing on screen.

The supplied asset's own ground is **`#F7F7F7`, not pure white**. Laid on a
pure-white plate it would show a 1.07:1 step at the image edge — faint on a
laptop, visible on a projector. `eklakshya-alpha.png` carries no ground at all,
which is why it is the asset named here.

#### Two alternatives, kept deliberately

| Asset | Use |
|---|---|
| `eklakshya-trim.png` | when the plate is `#F7F7F7` — the asset keeps its own ground |
| `eklakshya-knockout.png` | **no plate at all**; the mark sits directly on the slide. Preferred long-term |

#### Provenance, and its limit

`-alpha` and `-knockout` are **derived by threshold from a JPEG**. A script
decided which pixels were ground and which were wordmark. That is a computation
standing in for a judgement, and on a logo it is the kind of approximation a
brand owner notices before anyone else does.

**A vector original (`.ai`, `.eps`, `.svg`) or an official white-on-dark variant
replaces both.** Until one exists, do not use the derived files for anything
printed or client-facing without a look from whoever owns the brand.

---

## 8 · Verified contrast — all three themes

Measured, not estimated. Target ≥7:1; WCAG AA floor 4.5:1.

| Token | Navy | Blue | Green |
|---|---|---|---|
| title | 15.29 | 13.47 | 13.80 |
| body | 9.93 | 9.14 | **11.01** |
| level-3 text | 7.06 | 6.97 * | 8.91 |
| eyebrow | 6.12 * | 6.32 * | **8.48** |
| bullet marker | 5.61 * | 5.38 * | **8.48** |
| footer | 5.58 * | 5.12 * | 5.30 * |
| `state_a` amber | 7.34 | 6.46 * | 6.62 * |
| `state_b` cyan | 8.07 | 7.10 | 7.28 |
| `state_c` violet | 6.62 * | 5.83 * | 5.97 * |
| `focus` yellow | 11.05 | 9.73 | 9.97 |
| `warning` red | 5.51 * | 4.85 * | 4.97 * |

`*` = between 4.5:1 and 7:1 — passes WCAG AA, below our stricter target.
**Nothing fails.** Darkened green scores highest on text tokens.

### ⚠ Colour-blindness collision — applies to all three themes

Under deuteranopia simulation:

| Colour | Appears as |
|---|---|
| `state_a` amber `#F2A33C` | `#D9DE69` |
| `warning` red `#FF6B6B` | `#D7E06B` |

These are effectively identical. **`state_a` and `warning` must never appear
in the same diagram.** Options: drop the `warning` role (Deadlock content may
not need it), or reassign it to a hue far from amber.

### Resolution — channel assignment per role

The matrix shows the palette is **over-specified for colour vision**: five
colour-distinguished roles is more than the eye can carry once red–green
deficiency collapses everything onto a blue↔yellow axis. Cyan is the only
role that separates cleanly from all others.

Rather than dropping roles, each is assigned a **carrying channel**:

| Role | Carried by | Rationale |
|---|---|---|
| `state_a` | colour **+ dashed line** | primary semantic state |
| `state_b` | colour **+ solid line** | separates from state_a at 2.36:1 even simulated |
| `state_c` | colour **+ dotted line** | marginal on colour alone (1.46 vs state_a) |
| `focus_attention` | **glow / concentric rings**, colour secondary | collides with state_a (1.24:1) on colour |
| `warning_error` | **triangle icon**, colour secondary — **mandatory, not advisory** | identical to state_a (1.01:1) on colour |

### Why `warning` was not reassigned to a different hue

A search across the full HSV space was run for a replacement hue meeting
three conditions: ≥4.5:1 on all three backgrounds, separated from `state_a`
after deuteranopia simulation, and still reading as a warning.

| Family searched | Best worst-case separation from the other roles |
|---|---|
| red / pink / magenta (hues 320–360, 0–20) | **1.19:1** |
| best overall (teal / cyan, hues 176–196) | 1.59:1 — but collides with `state_b` and does not read as "warning" |
| current `#FF6B6B` | 1.01:1 |

*(1.00 = indistinguishable; ~1.50+ needed to be usefully distinct.)*

**No hue satisfies the constraint.** The cause is structural: all three themes
are dark, so `warning` must be light to hold contrast; light reds become
yellowish under deuteranopia; `state_a` is already yellowish. The colour space
has no room for a fifth distinguishable role.

`#FF6B6B` is therefore retained — it reads correctly for the ~94% with normal
colour vision — and the **triangle icon is the channel that actually carries
the distinction.** It is mandatory wherever `warning` and `state_a` could
co-occur.

**Rule: colour never carries meaning alone.** Every semantic distinction has a
second, non-colour channel. This satisfies VGR-02 (dimensions compose rather
than being picked one-at-a-time) instead of fighting it, and keeps diagrams
readable in greyscale, on a poor projector, and under any colour deficiency.

**Co-occurrence constraint:** `state_a` and `warning_error` must never appear
in the same diagram relying on colour to distinguish them — the shape/icon
channel is what separates them.

---

## 9 · Animation defaults

| Token | Value | Basis |
|---|---|---|
| `reveal.default_duration_s` | 0.3 | |
| `reveal.easing` | ease-out | |
| `reveal.stagger_s` | 0.12 | between sibling items |
| `camera.default_duration_s` | 0.8 | |
| `camera.easing` | ease-in-out | |
| `camera.rule_1` | follows the narration subject | VGR-03 |
| `camera.rule_2` | never move camera and reveal in the same beat | VGR-03 |
| `state_motion.default_duration_s` | 1.1 | |
| `state_motion.usage_rule` | teach a mechanic only — never decorative | VGR-04 |
| `layering.rule` | dimensions compose on one element, not either/or | VGR-02 |
| `slide_transition.type` | `null` | deferred — keep simple, revisit after slide 1 |
| `slide_transition.duration_s` | `null` | deferred |

Durations are starting values — tune after slide 1 (Layer 7 feedback).

---

## 10 · Output encode

| Token | Value | Basis |
|---|---|---|
| `video_codec` | H.264 High Profile | TGT-003 |
| `video_bitrate_mbps` | 8–12 | TGT-004 |
| `audio_codec` | AAC | TGT-005 |
| `audio_channels` | 2 | TGT-006 |
| `audio_sample_rate` | 48000 | TGT-007 |
| `audio_bitrate_kbps` | 192–256 | TGT-008 |

---

## 11 · Decisions — resolved

| # | Decision | Resolution |
|---|---|---|
| 1 | Theme selection | **Runtime parameter.** Contract ships all three variants; prompt workflow states the theme, code passes it as a CLI argument. `theme_selected` stays `null` by design. |
| 2 | `warning` / `focus` roles | **Kept, moved to non-colour channels** (§8). Colour never carries meaning alone. |
| 3 | `math` style | **Dedicated style added** — Source Serif 4, italic variables, true subscripts. `code` remains Space Mono. |
| 4 | Grid | **Adopted** — 12 × 118px columns, 8 × 90px rows, 24px gutters. Replaces the fixed 2-column split. |
| 5 | Slide transition | **Deferred** — keep simple; revisit after slide 1. Values stay `null`. |
| 6 | Full-screen legibility | **Verified.** Confirmed on a real 1080p display; 25px and 20px styles read acceptably. |
| 7 | Who binds a meaning to a slot | **Layer 6, at project level.** This document defines slots only. The binding is one-way (same meaning → same slot, every video), many-to-one (meanings may share a slot), and checkable (two meanings may share unless a viewer must tell them apart). See §4 and §4a. Closes OBS-005 |
| 9 | Footer contents | **Attribution left, brand mark right, no slide number.** A video has no navigation, so a slide number is dead weight on every frame. The mark needs a plate: its wordmark measures 1.32:1 on navy. See §7. |
| 8 | Payload version string | **Corrected.** The JSON payload read `"version": "v1"` through document versions v2 and v3 — the bump was simply missed. Document and payload were otherwise byte-identical, so nothing had drifted. Both now read v4. Closes OBS-006 |

### Reference specimen

`docs/shared/specimen/specimen-navy.html` is the canonical implementation of this contract
(`-blue` and `-green` differ only in the theme block; append `?grid` for the overlay).

- All four fonts render correctly (Space Grotesk, Inter, Space Mono,
  Source Serif 4) — TTFs bundled in `docs/shared/specimen/fonts/`.
- `math` style demonstrated with real subscripts:
  *P* = {*P*₁, *P*₂, … *Pₙ*} · *Pᵢ* → *Rⱼ* · *Needᵢ* ≤ *Work*
- Grid overlay toggles with `?grid` in the URL — cyan guides, never rendered
  in output.
- All five palette roles shown with their second channel.
- Theme is a CSS custom-property block at the top; the three variants
  (`_blue`, `_green`) differ only in that block.

### Remaining before first render

- `slide_transition.type` / `duration_s` — intentionally `null`, not blocking.
- Font installation on the render host (see below).

### Font provisioning

| Font | Use |
|---|---|
| Space Grotesk | h1–h3, eyebrow, panel labels, footer |
| Inter | body, caption, label |
| Space Mono | code, table cells |
| Source Serif 4 | math, math_variable, math_subscript |

TTFs are bundled at `docs/shared/specimen/fonts/`. Install with
`cp *.ttf ~/.fonts/ && fc-cache -f` on the render host, or keep the Google
Fonts `<link>` if that host has network access. Bundling is preferred for a
container — it removes a network dependency from the render path.

## 12 · JSON serialization

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "global_style_contract",
  "generated_at": "2026-08-16T00:00:00Z",
  "source": "layer_1_manual",
  "payload": {
    "version": "v6",
    "theme_selected": null,
    "canvas": {
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "safe_margin": {
        "top": 96,
        "right": 120,
        "bottom": 52,
        "left": 120
      },
      "spacing_base_unit_px": 4,
      "grid": {
        "columns": 12,
        "column_width_px": 118,
        "rows": 8,
        "row_height_px": 90,
        "gutter_px": 24,
        "content_area": {
          "width": 1680,
          "height": 888
        },
        "col_origin_fn": "120 + (n-1)*142",
        "row_origin_fn": "96 + (n-1)*114",
        "span_fn": "k*118 + (k-1)*24",
        "note": "invisible coordinate system — Layer 3 selects cells, does not invent pixel positions"
      },
      "satisfies": [
        "TGT-001",
        "TGT-002"
      ]
    },
    "type_scale": {
      "base_px": 31,
      "ratio": 1.25
    },
    "themes": {
      "navy": {
        "background": {
          "base_color": "#16234A",
          "accents": [
            "radial-gradient(circle at 12% 6%, rgba(120,150,220,0.28) 0%, transparent 22%)",
            "radial-gradient(circle at 78% 78%, rgba(90,120,200,0.30) 0%, transparent 30%)"
          ]
        },
        "text_secondary": "#C6D0EC",
        "text_tertiary": "#9FB0DA",
        "eyebrow": "#8FA3D9",
        "accent_marker": "#7C9BE8",
        "measured_body_contrast": 9.93
      },
      "blue": {
        "background": {
          "base_color": "#0B2E5C",
          "accents": [
            "radial-gradient(circle at 12% 6%, rgba(110,165,240,0.26) 0%, transparent 22%)",
            "radial-gradient(circle at 78% 78%, rgba(70,130,215,0.28) 0%, transparent 30%)"
          ]
        },
        "text_secondary": "#C6D6EE",
        "text_tertiary": "#A3BCE4",
        "eyebrow": "#8FB4E8",
        "accent_marker": "#6FA6F0",
        "measured_body_contrast": 9.14
      },
      "green_dark": {
        "background": {
          "base_color": "#26301C",
          "accents": [
            "radial-gradient(circle at 12% 6%, rgba(150,180,115,0.22) 0%, transparent 22%)",
            "radial-gradient(circle at 78% 78%, rgba(120,150,90,0.24) 0%, transparent 30%)"
          ]
        },
        "text_secondary": "#E3E7DE",
        "text_tertiary": "#CBD2C4",
        "eyebrow": "#EDC492",
        "accent_marker": "#EDC492",
        "measured_body_contrast": 11.01
      }
    },
    "palette_roles": {
      "text_primary": "#FFFFFF",
      "neutral_structure": "rgba(255,255,255,0.22)",
      "state_a": "#F2A33C",
      "state_b": "#3FD0C9",
      "state_c": "#B79CF5",
      "focus_attention": "#FFD84D",
      "warning_error": "#FF6B6B",
      "channels": {
        "state_a": {
          "colour": "#F2A33C",
          "redundant": "line_style:dashed"
        },
        "state_b": {
          "colour": "#3FD0C9",
          "redundant": "line_style:solid"
        },
        "state_c": {
          "colour": "#B79CF5",
          "redundant": "line_style:dotted"
        },
        "focus_attention": {
          "colour": "#FFD84D",
          "primary_channel": "glow_or_scale_pulse"
        },
        "warning_error": {
          "colour": "#FF6B6B",
          "primary_channel": "icon_or_shape_change"
        }
      },
      "rule": "colour never carries meaning alone — every semantic distinction has a non-colour channel",
      "note": "roles are NOT bound to entities here — Layer 4 binds them",
      "collision_warning": "state_a and warning_error are identical under deuteranopia (1.01:1); separation relies on the shape/icon channel"
    },
    "type_styles": {
      "eyebrow": {
        "family": "Space Grotesk",
        "weight": 500,
        "step": -2,
        "size_px": 20,
        "tracking": "0.1em",
        "transform": "uppercase"
      },
      "h1": {
        "family": "Space Grotesk",
        "weight": 600,
        "step": 3,
        "size_px": 60,
        "line_height": 1.15
      },
      "h2": {
        "family": "Space Grotesk",
        "weight": 600,
        "step": 2,
        "size_px": 48,
        "line_height": 1.2
      },
      "h3": {
        "family": "Space Grotesk",
        "weight": 500,
        "step": 1,
        "size_px": 39,
        "line_height": 1.25
      },
      "body": {
        "family": "Inter",
        "weight": 400,
        "step": 0,
        "size_px": 31,
        "line_height": 1.5
      },
      "body_emphasis": {
        "family": "Inter",
        "weight": 500,
        "step": 0,
        "size_px": 31,
        "line_height": 1.5
      },
      "caption": {
        "family": "Inter",
        "weight": 400,
        "step": -1,
        "size_px": 25,
        "line_height": 1.4
      },
      "label": {
        "family": "Inter",
        "weight": 500,
        "step": -1,
        "size_px": 25
      },
      "code": {
        "family": "Space Mono",
        "weight": 400,
        "step": -1,
        "size_px": 25,
        "line_height": 1.45
      },
      "code_keyword": {
        "family": "Space Mono",
        "weight": 400,
        "step": -1,
        "size_px": 25,
        "colour_role": "state_a"
      },
      "code_comment": {
        "family": "Space Mono",
        "weight": 400,
        "step": -1,
        "size_px": 25,
        "colour_role": "eyebrow"
      },
      "math": {
        "family": "Source Serif 4",
        "fallback": "Georgia, serif",
        "weight": 400,
        "step": 0,
        "size_px": 31,
        "line_height": 1.4
      },
      "math_variable": {
        "family": "Source Serif 4",
        "weight": 400,
        "style": "italic",
        "step": 0,
        "size_px": 31
      },
      "math_subscript": {
        "family": "Source Serif 4",
        "weight": 400,
        "style": "italic",
        "size_em": 0.62,
        "vertical_align_em": -0.25
      },
      "table_header": {
        "family": "Space Mono",
        "weight": 700,
        "step": -1,
        "size_px": 25
      },
      "table_cell": {
        "family": "Space Mono",
        "weight": 400,
        "step": -1,
        "size_px": 25
      },
      "panel_label": {
        "family": "Space Grotesk",
        "weight": 500,
        "step": -2,
        "size_px": 20,
        "tracking": "0.08em",
        "transform": "uppercase"
      },
      "footer_text": {
        "family": "Space Grotesk",
        "weight": 400,
        "step": -2,
        "size_px": 20
      }
    },
    "lists": {
      "level_1": {
        "marker": "filled_circle",
        "size_px": 12,
        "indent_px": 0,
        "gap_px": 34,
        "text_style": "body",
        "vertical_gap_px": 20
      },
      "level_2": {
        "marker": "hollow_circle",
        "size_px": 10,
        "stroke_px": 2,
        "indent_px": 44,
        "gap_px": 34,
        "text_style": "body",
        "vertical_gap_px": 20
      },
      "level_3": {
        "marker": "dash",
        "size_px": [
          10,
          2
        ],
        "indent_px": 88,
        "gap_px": 34,
        "text_style": "caption",
        "vertical_gap_px": 20
      }
    },
    "table": {
      "border": "1px solid rgba(255,255,255,0.15)",
      "cell_padding": "12px 20px",
      "header_fill": "rgba(255,255,255,0.06)",
      "rowhead_fill": "rgba(255,255,255,0.06)",
      "zebra_striping": false,
      "alignment_numeric": "right"
    },
    "code_block": {
      "background": "rgba(255,255,255,0.04)",
      "border_left": "3px solid",
      "border_left_role": "state_b",
      "padding": "20px 24px",
      "radius_px": 3
    },
    "footer": {
      "layout": "flex_space_between",
      "baseline_px": 52,
      "rule": "1px solid rgba(255,255,255,0.12)",
      "rule_offset_px": 22,
      "slots": [
        "attribution",
        "brand_mark"
      ],
      "colour": "rgba(255,255,255,0.55)",
      "attribution": {
        "text": "©Ravi Subramanian",
        "position": "footer left, inside the safe margin",
        "colour_note": "uses footer.colour — rgba(255,255,255,0.55), measured 5.58 / 5.12 / 5.30:1 on navy / blue / green",
        "symbol_note": "© is the COPYRIGHT SIGN, not @. Measured from the source video, where '©Ravi Subramanian' sits bottom-left on every frame including the intro and outro cards. An earlier draft of this contract read '@Ravi Subramanian'; @ denotes a handle or account, © denotes authorship of the work. The source was always right and the draft was a mis-hearing."
      },
      "brand_mark": {
        "src": "res/library/icons/eklakshya-alpha.png",
        "src_note": "The keyed variant, carrying no ground of its own. The supplied JPEG's ground is #F7F7F7, so laying it on a pure-white plate would show a 1.07:1 seam at the image edge — faint on a laptop, visible on a projector.",
        "aspect_ratio": 3.03,
        "aspect_note": "497x164 after trimming to content. The plate sizes itself from the mark, so replacing the asset with a different aspect needs no change here.",
        "height_pct_of_frame_width": 2.05,
        "height_px_at_1080p": 39,
        "plate": {
          "fill": "#FFFFFF",
          "radius_px": 4,
          "padding_pct_of_frame_width": {
            "vertical": 0.5,
            "horizontal": 0.8
          },
          "padding_note": "White must never touch the artwork, or the plate reads as a crop rather than a ground."
        },
        "position": "footer right, inside the safe margin",
        "why_a_plate_at_all": "MEASURED from the supplied asset: the wordmark is #000327 and scores 1.32:1 on navy #16234A, 1.50:1 on blue #0B2E5C and 1.46:1 on green #26301C. It is invisible on all three. On its own ground it scores 18.81:1. The mark therefore cannot sit bare on a dark slide in its supplied form — it needs either a light plate or a knockout.",
        "measured": {
          "wordmark_colour": "#000327",
          "supplied_ground": "#F7F7F7",
          "wordmark_on_own_ground": 18.81,
          "wordmark_on_navy": 1.32,
          "wordmark_on_blue": 1.5,
          "wordmark_on_green": 1.46,
          "plate_on_navy": 15.29,
          "plate_on_blue": 13.47,
          "plate_on_green": 13.8
        },
        "alternatives_kept": [
          {
            "asset": "res/library/icons/eklakshya-trim.png",
            "use": "when the plate is #F7F7F7 rather than white — the asset keeps its own ground"
          },
          {
            "asset": "res/library/icons/eklakshya-knockout.png",
            "use": "no plate at all; the mark sits directly on the slide. Preferred long-term"
          }
        ],
        "provenance_warning": "-alpha and -knockout are DERIVED BY THRESHOLD FROM A JPEG. A script decided which pixels were ground and which were wordmark; that is a computation standing in for a judgement. A vector original or an official white-on-dark variant replaces both.",
        "position_divergence": "The SOURCE deck places the mark centred in the footer band. This contract places it right, opposite the attribution. That is a deliberate change made after reviewing docs/shared/specimen/footer-themes.html, recorded here so the divergence is a decision rather than an oversight."
      },
      "slide_number_removed": "Slide numbers exist for navigation and a video has none — a viewer cannot turn to slide 4. The token cost a place on every frame and bought nothing. This removes the number from the SCREEN only: slide_id remains in every internal artifact and is how Layer 8 binds beats."
    },
    "animation_defaults": {
      "reveal": {
        "duration_s": 0.3,
        "easing": "ease-out",
        "stagger_s": 0.12,
        "variants": [
          "fade_in",
          "draw_on",
          "consume_text_to_diagram"
        ]
      },
      "state_motion": {
        "duration_s": 1.1,
        "variants": [
          "token_travel"
        ],
        "usage_rule": "teach a mechanic only — never decorative",
        "satisfies": [
          "VGR-04"
        ]
      },
      "camera": {
        "duration_s": 0.8,
        "easing": "ease-in-out",
        "variants": [
          "zoom_to_focus",
          "pan_between_regions",
          "pull_back_summary"
        ],
        "rules": [
          "camera follows the narration subject",
          "never move camera and reveal a new element simultaneously"
        ],
        "satisfies": [
          "VGR-03"
        ]
      },
      "layering": {
        "rule": "dimensions compose on one element, not either/or",
        "satisfies": [
          "VGR-02"
        ]
      },
      "slide_transition": {
        "type": null,
        "duration_s": null
      }
    },
    "output_encode": {
      "video_codec": "h264_high",
      "video_bitrate_mbps": [
        8,
        12
      ],
      "audio_codec": "aac",
      "audio_channels": 2,
      "audio_sample_rate": 48000,
      "audio_bitrate_kbps": [
        192,
        256
      ],
      "satisfies": [
        "TGT-003",
        "TGT-004",
        "TGT-005",
        "TGT-006",
        "TGT-007",
        "TGT-008"
      ]
    },
    "required_fonts": [
      "Space Grotesk",
      "Inter",
      "Space Mono",
      "Source Serif 4"
    ],
    "verification": {
      "contrast_measured": true,
      "colourblind_checked": true,
      "typography_legibility_verified_fullscreen": true
    },
    "entity_grammar": "NOT DEFINED HERE — Layer 6 (visual vocabulary) owns the meaning-to-slot binding. See payload.slot_binding. The previous value pointed at 'Layer 4' under the pre-renumber scheme and resolved to the transcript layer.",
    "slot_binding": {
      "rule_direction": "The same meaning takes the same slot in every video. The same slot MAY carry different meanings in different videos. One-way, on purpose.",
      "rule_sharing": "Two meanings may share a slot unless a viewer would ever need to tell them apart. Sharing is expected, not exceptional — the slots are three distinguishable groups, not a budget of three ideas.",
      "slots_are_unbound": [
        "state_a",
        "state_b",
        "state_c"
      ],
      "slot_names_are_deliberately_empty": "state_a/b/c carry no meaning and must not be renamed to one. Naming a slot 'blocked_waiting' forces a rename across every artifact the day a topic needs that slot for something else.",
      "owner": "layer_6_visual_vocabulary",
      "owner_scope": "project-level, extended per topic, never contradicted. A meaning used by more than one topic (e.g. 'blocked') is decided once; per-topic files could otherwise disagree and break the one-way rule.",
      "binding_table_requirement": "Layer 6 must list every meaning bound to each slot, so one reviewer pass can ask of each slot: could any two of these ever need distinguishing?",
      "contract_bindings": [
        {
          "token": "type_styles.code_keyword.colour_role",
          "slot": "state_a",
          "reason": "a keyword is a keyword in every topic — typography, not subject matter"
        },
        {
          "token": "type_styles.code_comment.colour_role",
          "slot": "eyebrow",
          "reason": "same reasoning; eyebrow is a text token, not one of the three slots"
        },
        {
          "token": "code_block.border_left_role",
          "slot": "state_b",
          "reason": "the edge marks 'this is code' — a document-wide category, not a topic's idea"
        }
      ],
      "contract_bindings_note": "Declared here, not relocated — the tokens stay where the loader reads them. The defect was that these bindings were invisible, not that they were in the wrong place.",
      "known_interaction": "Code-block keywords are already state_a. A topic binding state_a and applying it to a code block's border yields amber keywords in an amber-bordered box. Different visual categories, so probably fine — but that call belongs to the binding table, and nothing surfaces it today."
    }
  }
}
```

---

## Changelog

- **v6** — attribution corrected from `@Ravi Subramanian` to **`©Ravi Subramanian`**.
  Measured from the source video, where the copyright notice sits bottom-left on
  every frame. `@` denotes a handle; `©` denotes authorship of the work. Also
  recorded: the source deck places the mark **centred** in the footer band while
  this contract places it **right** — a deliberate change, now stated as one
  (OBS-039).

- **v5** — footer carries the institute mark. `footer.slots` becomes
  `["attribution", "brand_mark"]`: the slide number is removed because a video
  has no navigation, so the number occupied a place on every frame and bought
  nothing — `slide_id` is untouched in every internal artifact. The mark needs a
  light ground: measured against the supplied JPEG, the wordmark `#000327`
  scores **1.32:1 on navy**, 1.50 on blue, 1.46 on green, and 18.81 on its own
  ground. The supplied ground is `#F7F7F7`, so a pure-white plate would show a
  1.07:1 seam at the image edge — hence `eklakshya-alpha.png`, keyed to carry no
  ground. Height and padding are shares of frame width, not pixels. Two
  alternatives kept: `-trim` for an `#F7F7F7` plate, `-knockout` for no plate at
  all. Both derived variants are **threshold-derived from a JPEG** and are
  superseded the moment a vector original appears. `models.py` gains BrandMark,
  BrandPlate, BrandMarkMeasured and FooterAttribution, all optional on Footer so
  a v4 contract still validates without a migration. Specimen:
  `docs/shared/specimen/footer-themes.html`.

- **v4** — slots separated from meanings. §4 rewritten: `state_a/b/c` are slots and
  carry no meaning; the binding is **Layer 6's**, one-way (same meaning → same slot
  in every video), many-to-one, and checkable (two meanings may share a slot unless
  a viewer must tell them apart); the binding is project-level and topic-extensible
  so a meaning shared by several topics cannot drift. New §4a declares the three
  bindings this contract itself makes — `code_keyword`, `code_comment`,
  `code_block.border_left` — which were previously scattered and read as styling.
  Payload `version` corrected v1 → v4: it had been missed through v2 and v3 while
  document and payload stayed byte-identical, so nothing had actually drifted.
  Three stale layer references repointed from the pre-renumber scheme — the title
  (Layer 1 → Layer 2), §4's "is Layer 4", and `entity_grammar`'s "see Layer 4".
  Closes OBS-005 and OBS-006.

- **v3** — reference specimen `docs/shared/specimen/specimen-navy.html` built and verified
  with real fonts. `warning` hue reassignment attempted and rejected: an HSV
  search found no colour meeting the constraints (red/pink ceiling 1.19:1);
  `#FF6B6B` retained with the triangle icon channel made mandatory. Font TTFs
  bundled. Theme variants implemented as a CSS custom-property block.

- **v2** — grid adopted (12×118 cols, 8×90 rows, 24px gutters) replacing the
  fixed 2-column split. Dedicated `math` style added (Source Serif 4, italic
  variables, true subscripts); `code` unchanged. Palette roles assigned
  carrying channels so colour never carries meaning alone; `focus` and
  `warning` moved to glow and icon channels respectively. Full-screen
  legibility verified — contract approved. Theme selection confirmed as a
  runtime parameter.

- **v1** — initial contract. Three theme variants specified and contrast-verified.
  Type scale formalised (base 31, ratio 1.25) and h1 snapped 62 → 60.
  Added `code` / `math` / `table_*` styles for V029 matrices and V030 pseudocode.
  Footer opacity raised 0.42 → 0.55 (3.84:1 → ~5.3:1).
  Green base darkened `#3B4A2C` → `#26301C` for contrast headroom.
  Original tan accent `#D9A25E` (4.21:1) replaced with `#EDC492` (8.48:1).
