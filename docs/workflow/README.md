# Lecture Alive AI — Workflow — Playbook

**This file is the index.** It holds the aim, the rules, the layer map, and the
working constraints. It holds **no prompt text, no schemas, and no requirement
values** — those live in their own files and are cited from here.

---

## Notation — short forms and where they live

Every requirement in this project carries a prefixed ID. The prefix tells you
which register it belongs to, and therefore **which file to open**.

| Short | Full form | What it is | File |
|---|---|---|---|
| **TGT** | Delivery Target | A number measurable on the finished video file, after render | `delivery-targets.md` |
| **VGR** | Visual Grammar Rule | A rule about *how* content is generated; cannot be checked by inspecting the output file | `visual-grammar.md` |
| **RC** | Root Cause finding | Explains *why* something failed, in a way that changes how the fix must be built | `findings-and-decisions.md` |
| **DEC** | Open Decision | Needs a human choice before it can be closed | `findings-and-decisions.md` |
| **PROP** | Proposal | Suggested, not yet adopted | `findings-and-decisions.md` |
| **OBS** | Observation | Inbox item needing action; promotes to one of the above | `open-items.md` |
| **DEF** | Defect | A prompt that needed more than one round to give the right output | Layer 9 |

**Other terms used throughout**

| Term | Meaning |
|---|---|
| **Gate** | An automatic check that **blocks** a stage from completing if it fails. Downstream stages do not run |
| **Advisory** | The same check, but failure is only logged — the stage still completes |
| **fps** | Frames per second |
| **ffmpeg / ffprobe** | Command-line tools that process and inspect video and audio |
| **LUFS** | Loudness Units Full Scale — the standard measure of perceived loudness |
| **WCAG AA** | The accessibility standard for text contrast |
| **Forced alignment** | Matching a known transcript to audio to get per-word timings |

*File renaming (e.g. `delivery-targets-tgt.md`) was considered and deferred —
this table serves the same purpose without breaking citations in six other
documents.*

---

## 1 · Project objective

> You are a senior professor with recorded lectures — time-based transcript plus
> the original slides. Convert the slides into **guided animation** so the
> session becomes interactive and the visuals stay in sync with the narration.

**The invariant.** Narration *content* is fixed. Voice quality may improve; the
words and their timing must not change. Every layer is subordinate to this.

**Deliverable set:** 5 videos, each with its own PPTX.
**The table order is the delivery sequence.**

| Order | Video | Topic | Duration |
|---|---|---|---|
| 1 | V017 | OS · Bounded Buffer Problem | 8 min |
| 2 | V018 | OS · Reader Writer Problem | 17 min |
| 3 | V028 | OS · Banker's Algorithm Overview | 4 min |
| 4 | V029 | OS · Banker's Algorithm Data Structures | 8 min |
| 5 | V030 | OS · Safety Algorithm | 12 min |

---

## 2 · Objective of this document

| | Objective | Status |
|---|---|---|
| **Primary** | Produce the five enhanced videos **by hand, using prompts** | Deadline-bearing |
| **Secondary** | Capture whatever from each layer is genuinely useful for building the code pipeline — **in whatever form is useful, not necessarily JSON** | Best effort |

The primary objective is the deadline. The secondary objective is taken where it
is cheap and skipped where it would cost the deadline — but it is never
*invented later*, because it cannot be reconstructed after the fact.

**What the secondary objective is not:** it is not a demand for strict JSON at
every layer, and it is not the place to decide which fields a future module
requires. That is a Track 1 design question, answered later *using* these
artifacts as input. Here, a findings note is a perfectly good artifact.

---

## 3 · The four rules — every layer has these parts

A layer is not complete until all four exist.

| # | Part | Requirement |
|---|---|---|
| 1 | **What it does** | Why the layer exists, and which decision it owns |
| 2 | **The prompt to run** | Verbatim, in one copyable block, versioned. Re-runnable by anyone |
| 3 | **What it emits** | **Two forms** — one to decide with, one to build from. See below |
| 4 | **Review before proceeding** | Check the output against what the *next* layer needs, before running it |

**A layer missing its prompt is not "done" — it is undocumented.** Even when the
work was already completed by hand, the prompt is written down, because the
prompt is how the layer survives a re-run, a new video, or a new person.

### On rule 3 — every layer emits two forms

| Form | For | Shape |
|---|---|---|
| **Decide with** | A human approving or rejecting the output, fast | A table, a sketch, or a rendered page |
| **Build from** | The next layer, and eventually the code pipeline | JSON, or whatever the consumer parses |

| Layer | Decide with | Build from |
|---|---|---|
| 3 · Assets | Table: element, type, text, tag | `manifest.json` |
| 4 · Transcript | Table: time, text, word spans | `transcript.json` |
| 5 · Representation | Annotated table + layout sketch | `representation.json` |
| 6 · Vocabulary | Rendered swatch sheet | `vocabulary.json` |
| 8 · Sequence | **HTML player** — transport, captions, speed control | `sequence.json` |

**The rule that makes this safe: the decide-with form is a *view* of the
build-from form, generated from it — never authored alongside it.** Two
independently written descriptions of the same beats will drift, which is the
failure this whole structure exists to prevent. Where practical the view should
literally load the artifact.

**Why this is not optional.** Nobody can look at
`{"t_start_s": 66.0, "dimension": "state_motion"}` and know whether it feels
right. A beat sheet is approved by watching it, not by reading it — an
unreviewable artifact gets approved wrong and the error surfaces at render, two
layers downstream. The proven instrument here is the dry-run HTML: transport
controls, a caption bar showing the narration as it plays, and a speed control
for when you only want the shape of it.

This also inverts the cost. If the reviewable form is *generated* from the
machine form, the JSON stops being overhead and becomes load-bearing — and the
review instrument arrives free.

### On rule 3 — how to define an artifact without guessing

You cannot know an artifact's shape before running the layer once. So don't try.

| Part | Contains | Frozen? |
|---|---|---|
| **Required** | Only the fields the *next layer* cannot run without | Yes |
| **Observed** | Everything else the run happened to produce | No — append freely |

- The test for Required is narrow: **does the next layer read this field?** Not
  "might this be useful someday." Required should end up small.
- **Write the artifact spec after the first run, not before.** The example in a
  layer file must be *real output*, never invented.
- After the first slide, promote anything from Observed that the next layer
  actually used into Required. That is the one revision window. Then it locks.
- **JSON only where something parses it.** If no code and no later prompt reads
  it, it does not need a schema — prose or a table is correct.

### On rule 4 — the review checkpoint

This section lives at the **end of layer N's file**, not the start of N+1's,
because that is when it is read, and it makes layer N responsible for handing
over something usable.

At the checkpoint, ask three things:

1. Does the next layer's prompt still make sense given this output?
2. Does this output contradict a decision made in an earlier layer?
3. Did anything come out semantically empty — a placeholder that satisfies the
   words of the prompt but carries no meaning?

If the answer to any of these is yes, fix it **before** running the next layer.

---

## 4 · Prompt-quality rules

Iteration count is a cost — time, tokens, and losing the thread. These exist to
drive it toward one round.

| # | Rule |
|---|---|
| 1 | **Put the example inside the prompt**, not below it as documentation |
| 2 | **Give every rule its reason.** A bare prohibition gets satisfied literally and creatively |
| 3 | **One prompt, one kind of judgement.** The tell you need to split is the phrase "and also" |
| 4 | **Constrain the input as well as the output** — "Use only: [IDs]. Ignore all others. If something outside that list seems relevant, name it and stop" |
| 5 | **Ask for reasoning before the value**, or the rationale becomes a justification of an answer already committed to |
| 6 | **Force an "UNRESOLVED / ASSUMPTIONS / FLAGS" section** in every output. This converts silent wrong output into a visible question |
| 7 | **Re-run a fixed prompt; do not patch in conversation.** By round three the context is anchored on two wrong answers |
| 8 | **When a prompt needed 3+ rounds, save the amended prompt** — not the output — to `prompt-changelog.md`. This is what makes video 2 cheaper than video 1 |
| 9 | **Give a fixed key set and forbid changing it.** Where the output has known structure, supply the keys and say: *fill values only — do not add, rename, reorder, or omit keys.* This turns a generative task into a fill task and removes structural variance between runs |
| 10 | **Forbid silence.** Every key gets a value, or `null` **with a one-line reason**. A key quietly left out reads as "not applicable" when it usually means "not considered" |

---

## 5 · What this document is not

**It is not the home of any specification.** Rule: **exactly one owner per
fact.** Any number, rule, or table appearing in two places is a defect, not a
convenience.

| Content | Lives in | Here we |
|---|---|---|
| Requirements and targets | `shared/requirements/*.md` | **cite the ID** — write "per TGT-001", never `1920x1080` |
| The style contract | `specs/style-contract.md` + its JSON | **cite path + version** — never paste the content |
| Prompts and layer flow | **here** | own it |
| Artifact register | `artifacts.md` | own it |
| Open observations | `open-items.md` | own it |
| Amended prompts | `prompt-changelog.md` | own it |

**Why it matters, concretely.** The value `1920` currently exists in five files.
Change it in one and four are silently wrong. A citation cannot go stale; a copy
always does. The style contract already proves this — the document says v3 while
the shipped JSON says v1.

---

## 6 · Layer map — a working hypothesis, not a plan

Prompts are written **just-in-time**, one layer at a time, so that each is
informed by the previous layer's actual output. Layers may be reordered, split,
or added as the work reveals complexity.

| # | Layer | Decides | Scope | File | Prompt | Work |
|---|---|---|---|---|---|---|
| 1 | Target spec | What the output must be | Project | `1-target-spec.md` | v1 | done |
| 2 | Global theme | Background, palette roles, typography, animation defaults | Once, all 5 | `2-global-theme.md` | v2 | done |
| 3 | Asset deconstruction | What is in each deck | **Per deck** | `3-asset-deconstruction.md` | v4 | verified on 1 slide |
| 4 | Transcript + timing | What is said, when | Per video | — | planned | — |
| 5 | Slide representation | Semantic identity; layout | Per slide | — | planned | — |
| 6 | Visual vocabulary | What each semantic type looks like | Per topic | — | planned | — |
| 7 | Audio mastering | Delivered sound quality | Per video | — | planned | — |
| 8 | Sequence / beats | Timed beats bound to narration | Per slide | — | planned | — |
| 9 | Defects & automation boundary | What is worth automating | Project | — | planned | — |

Only rows with a **file** exist. The rest are intent.

**Known state.** Layers 1 and 2 have completed *work*; their prompts are now
written here. This file supersedes `docs/workflow/playbook.md`, and
`2-global-theme.md` supersedes
`docs/workflow/layer-captures/layer1-token-schema-and-prompt.md` — both of which
used the old layer numbering (theme = Layer 1).

### Numbering governance

- Layer numbers start at **1** and are **strictly sequential** — no gaps, no
  letter suffixes.
- File names carry the same number: `1-target-spec.md`, `2-global-theme.md`, …
- If a layer is inserted, the following layers are **renumbered and their files
  renamed**, and the move is recorded in the changelog below.
- Renumbering means every citation of a layer number must be updated with it.
  Because prompts are written just-in-time, few files exist at any moment, so
  this stays cheap — but it is a real cost, so insert deliberately.

### Two independent branches

- **Layers 3 ∥ 4** run concurrently — they share no inputs.
- **Layer 7 (audio)** is a parallel branch that gates nothing upstream and
  rejoins only at final mux.

---

## 6a · Tooling — `mpk`

Deterministic work belongs in a tool; judgement belongs in a prompt. `mpk`
(Media Pipeline Kit, `tools/mpk.py`) is where the deterministic half lives.

```
mpk --help                 every group and command has -h
mpk deck   info | extract | normalize | merge | render
mpk review build
mpk audio  extract | asr | probe
mpk video  probe | uniquefps
mpk check  manifest
```

| Command | Serves |
|---|---|
| `deck extract` | Layer 3 step 1 — OOXML shape tree, `lines[]`, connector endpoints, `id_coverage` |
| `deck normalize` / `merge` | Repairing a deck before extraction — e.g. a slide reconstructed at the wrong canvas size |
| `review build` | Layer 3 step 3A — injects the manifest into `tools/templates/slide-review.html` |
| `audio extract` / `asr` | The RC-003 two-path split: 48 kHz stereo master, 16 kHz mono for alignment |
| `audio probe` | Layer 7's input measurements |
| `video uniquefps` | **TGT-013** — unique frames per second, which TGT-002 cannot detect |

The rule: **a prompt never does arithmetic a file already contains.** Geometry,
text, indent levels and connector endpoints are explicit in the `.pptx`; reading
them from a picture converts known values into guesses.

---

## 7 · Working constraints

### Attachment limits

| Limit | Value |
|---|---|
| File size, chat upload | 500 MB per file |
| Files per chat | 20 |
| PDF pages | 1000 max; visual elements analysed only up to 100 pages |
| Image dimensions | up to 8000×8000; 1000×1000 or larger recommended |
| Project files | 30 MB per file, unlimited count, must fit the context window |
| Video / audio uploads | **not supported** |

**The real constraint is the context window, not file size.** The registers plus
a transcript plus a manifest will exhaust context long before any file
approaches a size limit. This is why every prompt scopes its inputs by ID.

### Video and audio are never prompt inputs

| Layer | What it actually consumes | Attach? |
|---|---|---|
| 3 | one slide, as an image | yes — small |
| 4 | text, produced locally by ffmpeg + forced alignment | yes — text |
| 7 | measurements from `ffprobe`, not the audio itself | numbers only |
| 8 | text artifacts (representation, vocabulary, transcript) | yes — text |
| render / mux | video and audio files | **never** — scripts do this |

### Chunking

| Stage | Unit | Why |
|---|---|---|
| Prompting, planning, rendering | **per slide** | Layers 3, 5 and 8 are per-slide already |
| Audio mastering | **whole video, never chunked** | Loudness is integrated across the program; chunk-then-concatenate produces audible level jumps |
| Final assembly | concatenate slide renders, then mux the single mastered track | — |

**Cuts happen only at slide boundaries, never mid-beat** — otherwise a camera
move or token travel is split across two renders and the seam is visible.

---

## 8 · Tracking files

| File | Holds | Growth |
|---|---|---|
| `context.md` | The standing project brief, attached to every layer run | rarely — every addition is paid for on every run |
| `tools/templates/*.html` | The review pages themselves; `mpk review build` only injects data. One per review kind | one per layer that needs a view |
| `artifacts.md` | Every artifact: path, form, produced by, consumed by, scope, version, status | append per artifact |
| `open-items.md` | `OBS-xxx` observations needing human action | append; closed by promotion |
| `prompt-changelog.md` | Amended prompts, with the round count that triggered the amendment | append per amendment |
| `capture-log/` | One file per slide: what was run, what came out, what broke | one per slide |

### Where an observation goes

The test: **does the next prompt need this, or does a human need to act on it?**

| | Goes in | Consumed by |
|---|---|---|
| Content-level — "narration mentions a wait queue with no visual" | the prompt's own `UNRESOLVED / ASSUMPTIONS / FLAGS` output | the next layer |
| Process-level — "the style contract has no pacing block" | `open-items.md` as `OBS-xxx` | a human |

**Promotion path.** `open-items.md` is an inbox. When an observation turns out
to be a real requirement, it graduates to a TGT / VGR / RC id in the Layer 1
registers, and the OBS row is closed with a pointer to that id.

---

## 9 · Working order

1. **Write the layer's prompt** — informed by the previous layer's real output
2. **Review the prompt** before running it
3. **Run it in a fresh chat** — see below
4. **Review before proceeding** (rule 4)
5. If it took 3+ rounds → amend the prompt, log it in `prompt-changelog.md`
6. Record what was produced in `artifacts.md`; record what needs action in `open-items.md`
7. Only then write the next layer's prompt

### Two run modes — verification and production

| Mode | Where | When |
|---|---|---|
| **Verification** | A **fresh chat**, no prior context | The first time a layer's prompt is run, and after any amendment |
| **Production** | **One chat per slide**, carrying the whole per-slide chain | Every run after that |

**Verification — why a fresh chat.** A prompt written and run in the same
conversation is tested against a reader who already knows the project. It will
appear to work while quietly depending on context that is not in the prompt.
The fresh chat is the only honest test of rule 2, "re-runnable by anyone."

Attach exactly: `context.md`, the registers the prompt's scope line names, and
the layer's input artifacts. Nothing else.

**If a fresh run fails for lack of context, the prompt is wrong, not the
chat.** Fix the prompt — or `context.md`, if the gap is genuinely shared —
rather than explaining the missing piece in conversation. An explanation given
in chat is lost; a fixed prompt is kept.

**Production — why one chat per slide.** Layers 3 → 5 → 6 → 8 are a chain over
the same slide: each reads what the last produced. Re-establishing that context
at every step is pure cost, and the earlier output is exactly the context the
next step needs. Run the chain in one conversation.

| Layer | Run mode |
|---|---|
| 1, 2 | Once, project-wide. Output feeds in as an attachment |
| 4 | Once per video, independent of the slide chain |
| 7 | Once per video, parallel branch |
| **3 → 5 → 6 → 8** | **The per-slide chain — one chat per slide** |

`context.md` earns its place by making verification possible. It is attached on
every verification run and at the start of each production chain — not at every
step within one. Keep it short regardless.

**One slide end-to-end before touching slide two.** Doing this means eating the
contract revision once instead of propagating a wrong decision across five
videos. Expect Layers 2 and 6 to be revised after the first slide — that is the
single revision window, after which they lock.

Videos are produced in the delivery sequence given in section 1.

---

## 10 · Definition of done

| # | Condition |
|---|---|
| 1 | All five videos delivered and passing the Layer 1 acceptance criteria |
| 2 | Every layer that was run has all four parts written down |
| 3 | `open-items.md` has no open row that blocks a delivered video |
| 4 | `artifacts.md` lists what Track 1 receives, and where it is |

Conditions 1 and 3 are the primary objective. Conditions 2 and 4 are the
secondary objective and are satisfied *as the work happens*, not retrofitted.

---

## Changelog

- **v1** — restructured from the single-file playbook. Aim restated as primary
  (videos) / secondary (pipeline artifacts). Four-part layer rule adopted, with
  "review before proceeding" added as a first-class part. Prompt-quality rules
  added. Prompts moved to just-in-time authoring in per-layer files. Tracking
  split into `artifacts.md`, `open-items.md`, `prompt-changelog.md`. Layers
  renumbered to start at 1 and run strictly sequentially (old Layer 0 → 1;
  old L2A/L2B → 3/4; old 5/6/7 → 7/8/9). Pilot-video approach dropped in favour
  of the delivery sequence.
