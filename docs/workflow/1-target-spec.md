# Layer 1 — Target Spec

**Scope:** project · **Prompt version:** v1 · **Work status:** complete
**Emits:** the four Layer 1 register files (see §3)

> **Note on this prompt.** Layer 1's *work* was completed before this playbook
> existed, and the prompt originally used produced a different, flatter output
> (a single `DIFF-001…005` table). That prompt would not reproduce what Layer 1
> actually became. The prompt below is **written from the delivered outcome**,
> taking what was useful from the original. It has not been run end-to-end; it
> exists so the layer is re-runnable — for a new customer, a new deck, or a
> revision — and so its reasoning survives.

---

## 1 · What it does

Establishes **what the finished output must be**, before anything is designed or
built.

It converts a three-way comparison — the original lecture recording, our
previous output, and the competitor's output — into a set of **citable,
ID'd requirements** that every later layer is measured against.

**The decision this layer owns:** what counts as acceptable, and what does not.

**What it does not own:** how anything is achieved. No theme, no vocabulary, no
timing. A requirement here says *what must be true of the output*, never *how to
make it true*.

**Why the three-way comparison is evidence, not the artifact.** The measurements
are retained so any requirement can be traced back to what justified it — but a
measurement table is not a requirement. The requirement is what you decided
because of it.

---

## 2 · The prompt to run

Two steps. **Do not collapse them.** Step 1 produces facts; step 2 makes
decisions from them. Collapsing the two produces requirements that quietly
encode an opinion as a measurement.

### Step 1 — evidence

```
INPUTS: three video files — (a) the original lecture recording,
(b) our previous output, (c) the competitor's output. Plus any client
feedback, quoted verbatim.

Produce a three-way comparison. Two parts.

PART A — measured properties. For each of the three videos, report:
duration, resolution, frame rate, video codec and profile, video bitrate,
audio channels, audio sample rate, audio bitrate, audio mean volume, audio
peak. Use ffprobe and volumedetect. Give the command used for each figure.

PART B — observed properties. For each of the three videos, describe:
semantic fidelity (is technical notation preserved or simplified away),
visual grammar consistency, which animation dimensions are used (element
reveal / motion within the diagram / camera movement), text rendering
defects, pacing and dead air, and content coverage against the narration.

RULES:
- Report only what you measured or directly observed in these three files.
  Do not generalise from general knowledge of video production, and do not
  import best practices. This step is facts only, because a fact that is
  actually an opinion cannot be traced back or argued with later.
- Where a property cannot be measured, say so explicitly. Do not estimate.
  An estimate presented as a measurement will be cited as one.
- Report where OUR output is BETTER, not only where it is worse. A strength
  is as important as a deficit — it becomes something to protect rather
  than something to fix.
- Do NOT propose fixes, targets, or solutions. That is step 2.
- Tag every observation with its source: measured / original / ours /
  competitor / client feedback.

End with:
UNRESOLVED — what you could not measure or observe, and why
ASSUMPTIONS — anything you decided without instruction
FLAGS — anything that contradicts another input
```

### Step 2 — classify into registers

```
INPUTS: the step 1 evidence, and the client context.

Turn each observation into a requirement, sorted by SPECIES. For every
observation, state your reasoning FIRST, then the classification, then the
requirement text — in that order, so the classification is reached rather
than justified.

THE FOUR SPECIES — use this test, in this order:

  TGT — Is it a number you can measure on the finished file after render?
        (resolution, fps, codec, bitrate, loudness, duration)
        -> Register A, delivery-targets.md

  VGR — Is it a rule about HOW content is generated, which cannot be
        checked by inspecting the output file alone?
        (what may be dropped, how motion is used, what drives the camera)
        -> Register B, visual-grammar.md

  RC  — Does it explain WHY something failed, in a way that changes how the
        fix must be built?
        -> Register C, findings-and-decisions.md

  DEC / PROP — Is it unresolved: needs a human choice, or needs a
        measurement not yet taken?
        -> findings-and-decisions.md

RULES:

- ONE REQUIREMENT PER MEASURABLE PROPERTY. Never bundle. "Raise the output
  encode targets" is not one requirement, it is eight — and a bundled row
  cannot be individually validated, cited, or retired.

- BEFORE WRITING A TARGET, ASK WHETHER THE OBVIOUS FIX WOULD ACTUALLY WORK.
  If raising the number would not fix the observed defect, the real finding
  is a root cause (RC), not a target. Worked example: our output was choppy
  at 8 fps. Raising the EXPORT frame rate would not help, because export
  cannot add motion detail that was never rendered internally. So the
  finding is "internal render fps is distinct from export fps" — an RC that
  points at the animation engine — and NOT a target of "export at 30 fps".
  This test is the highest-value part of this step: it prevents a whole
  class of fix that looks right and changes nothing.

- RECORD STRENGTHS AS CONSTRAINTS. Where our output is already better, the
  requirement is to protect it. Give it status `constraint`, not `adopted`.

- STATE THE COMPETITIVE BAR EXPLICITLY. Is the competitor's production
  quality something to MEET, or to EXCEED? Answer from the client context,
  not from ambition. This single line scopes every later layer, because it
  decides when work stops.

- DO NOT GUESS A VALUE YOU HAVE NOT MEASURED. Leave it null and name what
  must be measured and from which source. A guessed threshold gets adopted
  and then defended.

- Where a requirement depends on a decision nobody has made yet, write it
  as DEC, name what blocks it, and list the options with their costs. Do
  not pick one.

ID RULES: assign sequentially within each species (TGT-001, VGR-01, RC-001,
DEC-001, PROP-001). IDs are immutable and append-only — never renumber,
never reuse. Retire by status, never by deleting a row: a deleted row
leaves dangling citations and erases the reasoning.

STATUS VOCABULARY: adopted | constraint | proposed | rejected | superseded

OUTPUT — four files.

1. delivery-targets.md   — Register A
   | ID | Property | Target | Owner (pipeline section) | Status |
   Example row:
   | TGT-007 | Audio sample rate | 48 kHz | Transcript Alignment >
     Audio Preprocessing | adopted |

2. visual-grammar.md     — Register B
   | ID | Item | Pipeline Module(s) | Description | Impact on quality |
   Example row:
   | VGR-03 | Camera movement is narration-driven | Rendering & Composition
     | Pan, zoom and focus changes must be tied to what is currently being
     said — never decorative motion added for visual interest | Undirected
     camera motion is actively distracting in instructional content |

3. findings-and-decisions.md — Register C + open items
   | ID | Finding | Implication | Owner | Status |
   plus a section per DEC and PROP giving the options and their costs.

4. competitive-analysis.md — the step 1 evidence, retained as provenance,
   plus the client context and the competitive bar decision.

Each file ends with a machine-readable JSON slice carrying id, property,
target, owner and status — the minimum a later layer needs to cite. The
tables are primary; the JSON is a thin slice, not a second copy of the
prose.

End every file with:
UNRESOLVED / ASSUMPTIONS / FLAGS
```

---

## 3 · What it emits

**Form:** human-readable tables, primary. Layer 1 is a decision record, not a
machine input — its consumer is a human writing later prompts, plus validation
code that reads only the IDs and values.

### Required — frozen

| Field | Why |
|---|---|
| `id` | Every later layer cites it. Immutable |
| statement | The target, rule, or finding |
| `owner` | Which pipeline section is accountable |
| `status` | How a requirement is retired without deleting it |

Four files, one per species group:

| File | Holds | Consumed by |
|---|---|---|
| `delivery-targets.md` | TGT — numeric, post-render | validation gates; Layers 2, 7 |
| `visual-grammar.md` | VGR — behavioural, generation-time | Layers 2, 3, 5, 6, 8 |
| `findings-and-decisions.md` | RC / DEC / PROP | Layers 4, 7, 8 |
| `competitive-analysis.md` | evidence and provenance | rarely read; traceability |

### Observed — open, append freely

Rationale, impact-on-quality prose, measurement commands, per-file
cross-reference sections, the machine-readable JSON slice.

### Governance

- IDs immutable and append-only.
- Retire by `status`, never by deleting a row.
- **Register B rule text is edited only in `visual-grammar.md`.** Everywhere
  else cites `VGR-xx`.
- Any document stating a number must cite the TGT id, not repeat the number.

---

## 4 · Review before proceeding

Run these checks against the actual output before writing Layer 2's prompt.

| # | Check |
|---|---|
| 1 | Is every TGT actually measurable on the finished file? A row that needs judgement is a VGR wearing a number |
| 2 | Does every VGR name the module that owns it? An unowned rule is never implemented |
| 3 | Is any row bundled — one ID covering several independently checkable properties? |
| 4 | Does any RC have no owner and no gate? A root cause nobody owns is a defect that ships |
| 5 | Is any DEC blocking a layer we are about to run? |
| 6 | Did anything come out semantically empty — a placeholder that satisfies the prompt's words but carries no meaning? |

### Known open at the time of writing

These were found by running the checks above against the delivered Layer 1
output. They are tracked in `open-items.md`, not fixed here.

| Check | Finding |
|---|---|
| 4 | **RC-001** (internal render fps ≠ export fps) has an owner but **no gate**. Nothing detects an 8 fps internal render that is upsampled to 30 fps on export — so the single worst defect in the competitive analysis passes every check |
| 2 | **VGR-06** and **VGR-07** are marked `needs_validation_gate: true` with no implementation. This becomes blocking at Layer 8, which is the first layer producing something they could check |
| 5 | **DEC-001** (word-timestamp source) is open but every later layer already assumes path A. It blocks Layer 8 |
| 1 | **PROP-001** threshold is `null` pending a measurement from the original lecture — material is available (120.1s), the measurement has not been taken |

### What Layer 2 needs from this layer

Layer 2 reads **VGR-02, VGR-03, TGT-001…004** only. Confirm those four are
unambiguous and need no interpretation before writing Layer 2's prompt.

---

## Changelog

- **v1** — prompt written from the delivered outcome. Split into two steps
  (evidence / classification) because the original single prompt mixed facts
  with decisions. Species-classification test added — the original produced one
  flat `DIFF` list, which is why encode requirements arrived bundled as a single
  row. "Would the obvious fix actually work?" test added, derived from how RC-001
  was found. Strength-as-constraint and competitive-bar rules added from the
  client context.
