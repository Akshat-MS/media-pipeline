# Prompt Changelog

**Append-only.** When a prompt needs more than one round to produce the right
output, the amended prompt is saved here — **not the output.**

**Why.** The finished video is the deliverable, but the fixed prompt is what
makes the second video cheaper than the first. Without this file, round counts
stay flat across all five videos instead of falling. See `README.md` §4, rule 8.

**Threshold.** Log any prompt that took **3 or more rounds**. One or two rounds
is normal and not worth the overhead.

---

## Entry format

Copy this block per amendment.

### PC-xxx · Layer N · prompt vN → vN+1

| | |
|---|---|
| **Date** | |
| **Rounds taken** | |
| **What went wrong** | What the prompt produced instead of what was needed |
| **Why** | The reason the original wording permitted it — this is the useful part |
| **The change** | The exact clause added, removed, or reworded |
| **Prompt-quality rule** | Which of the eight rules in `README.md` §4 it maps to, or "new rule" |

---

## Entries

### PC-000 · Layer 2 · the first repair — predates this playbook

Recorded from `docs/workflow/layer-captures/layer1-token-schema-and-prompt.md`,
written during the original work (when the theme layer was numbered 1). It is
the earliest prompt amendment in the project and the origin of rules 9 and 10.

| | |
|---|---|
| **Date** | before 2026-08-17 |
| **Rounds taken** | several — the document opens with "why previous attempts returned vague output" |
| **What went wrong** | The prompt returned vague prose; structure differed between runs; type sizes were arbitrary; values went missing without being marked; the result could not be judged; entity vocabulary bled in from Layer 6 |
| **Why** | The prompt asked for aesthetic judgement and concrete specification in the same breath, and supplied no structure for the answer — so each run invented one |
| **The change** | Split into choose-direction / fill-tokens / verify. **Supplied a fixed key set** with "fill values only — do not add, rename, reorder, or omit keys". Required sizes to derive from a declared modular scale. Required every token to carry a value or `null` with a reason. Required a specimen slide exercising every token |
| **Prompt-quality rule** | Origin of rule 9 (fixed key set) and rule 10 (forbid silence); also rule 3 (one kind of judgement per prompt) |

### PC-001 · Layer 2 · prompt v0 → v1

| | |
|---|---|
| **Date** | 2026-08-18 |
| **Rounds taken** | 3 (contract v1 → v2 → v3) |
| **What went wrong** | The prompt produced background, palette, typography and animation defaults only. The grid, the type scale, the separate `math` style, the measured contrast table, and the colour-blindness channel assignment all had to be added in later rounds |
| **Why** | The prompt asked for a theme to be *designed* but never asked for it to be *verified*. Every improvement across the three rounds — the green base darkened for contrast headroom, footer opacity raised 3.84:1 → 5.3:1, the amber/red collision under deuteranopia, the tan accent replaced 4.21:1 → 8.48:1 — came from measuring, not designing |
| **The change** | Added a whole middle step: **step 2, verify and measure** — contrast per token per theme, background uniformity, colour-vision simulation with per-shape-class second channels, replacement-hue search, full-screen legibility, grid reconciliation |
| **Prompt-quality rule** | Rule 3 (one prompt, one kind of judgement) — designing and verifying are different judgements and were being asked for at once |

### PC-002 · Layer 2 · palette role naming

| | |
|---|---|
| **Date** | 2026-08-18 |
| **Rounds taken** | not yet re-run — defect found at review, not at generation |
| **What went wrong** | The prompt asked for "the palette with a semantic role named per colour". The output was `state_a`, `state_b`, `state_c` — names that satisfy the instruction and carry no meaning. Nothing then prevents the same colour meaning "blocked" in one video and "granted" in another (OBS-005) |
| **Why** | The instruction stated *what to do* but not *why*, so it was satisfied literally. A bare instruction is always available to be met in the cheapest way |
| **The change** | Added the reason and a worked counter-example: *"A role name must state WHAT THE COLOUR MEANS… `blocked_waiting` is correct. `state_a` is NOT acceptable: it satisfies the instruction while carrying no meaning… If you cannot say what a colour means, it is not a role."* |
| **Prompt-quality rule** | Rule 2 (give every rule its reason) |
