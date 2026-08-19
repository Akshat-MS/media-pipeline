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

### PC-004 · Layer 3 · v1 → v4, before any deck run

| | |
|---|---|
| **Date** | 2026-08-19 |
| **Rounds taken** | 1 on the verification slide; three prompt revisions came from *inspecting* that output rather than from failed runs |
| **What went wrong** | Nothing failed. Four things were absent that only a real artifact reveals: notes existed in prose but not in the data; ID gaps were invisible; a label had no relationship to the shape it named; and `paragraphs[]` silently merged lines a viewer sees separately |
| **Why** | v1 was written before any run, so its field list was a guess about a shape that had not been produced. The playbook's own rule — *write the artifact spec after the first run* — is exactly what this proves |
| **The change** | v2 made the review table primary. v3 moved to deck scope and added `flags[]`, `entity_inventory`, `chrome_pattern`, `id_coverage`, `labels_prior`, table and group handling. v4 pointed step 1 at `mpk deck extract`, split step 3 into tool/prompt paths, and added `lines[]` for soft-broken lines |
| **Prompt-quality rule** | Rule 6 (force UNRESOLVED/FLAGS) is what surfaced three of the four. Rule 9's fixed key set is what the deck wrapper now provides |

**The finding worth remembering.** PowerPoint's `<a:br/>` soft breaks mean
`paragraph.text` returns `'lock = false;\x0bdo {\x0b    while tns(&lock);'` as
one string. Three code lines, one entry. Layer 8 reveals visual lines, so that
would have collapsed three reveals into one — and the failure would have looked
like a sequencing bug two layers downstream, not an extraction bug. Verified on
the real V017 deck: 8 visual lines across 6 paragraphs, in both code blocks.

### PC-003 · All layers · the two-form rule

| | |
|---|---|
| **Date** | 2026-08-18 |
| **Rounds taken** | n/a — found by inspecting the dry-run artifact, before any layer ran |
| **What went wrong** | Layers were specified to emit machine artifacts (JSON) only. A `sequence.json` cannot be reviewed by eye: nobody can read `{"t_start_s": 66.0, "dimension": "state_motion"}` and know whether it feels right |
| **Why** | The design optimised for the secondary objective (artifacts for the engine) and silently degraded the primary one (deciding fast and correctly). The dry run had it the other way round — every step produced something human-readable, which is why decisions were instant |
| **The change** | Every layer now emits **two forms**: a decide-with view and a build-from artifact, with the view **generated from** the artifact so the two cannot drift. Layer 8 inherits the dry run's HTML player — transport, caption bar, speed control |
| **Prompt-quality rule** | New. Rule 3 of the four-part layer rule was rewritten around it |

**Source.** The dry-run file `themed_final1.html` turned out to contain a
complete beat sheet inside `buildCues()` — start time, end time, target
element, action, narration text. The data existed all along; it was trapped in
the renderer instead of being emitted. The fix is not to produce new
information, it is to give what already exists somewhere to live.

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
