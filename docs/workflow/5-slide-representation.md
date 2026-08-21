# Layer 5 — Slide Representation

**Scope:** per video · **Prompt version:** v1 · **Work status:** not yet run
**Emits:** `<video>.representation.json` (build from) + `<video>.representation.html` (decide with)
**Tooling:** `mpk video slidechanges --deck` · `mpk review build` · `mpk check representation`

> **Layout is NOT in this layer.** `context.md` originally defined Layer 5 as
> *"what each element means; the slide's layout"*. Layout moved to **Layer 6**,
> where the chosen Direction fixes vocabulary and layout grammar in one decision.
> The reason is a one-way dependency: choosing a Direction needs the meanings —
> you only know a ring-with-pointers is wrong for this deck because the meaning
> list has no ring — while the meanings do not need the Direction. `enqueue`
> means *data moves into the buffer* whether it is drawn as an arrow, a pointer
> advancing, or a log line.

---

## 1 · What it does

**The first layer that decides anything.**

Layers 3 and 4 were forbidden to interpret. Layer 3 could see an arrow runs from
Producer to the buffer — geometry, certain — but not what the arrow *does*.
Layer 4 recorded what was said and when. Layer 5 is the first place the two meet.

| This layer answers | This layer does **not** answer |
|---|---|
| `v017_s03_84` is an `enqueue` | What an `enqueue` looks like — Layer 6 |
| Between 04:13 and 05:39 the subject is the producer code block | Which line reveals at 04:31 — Layer 8 |
| `BUFSIZE` and `n` are the same quantity | What colour that quantity is — Layer 6 |
| Nothing on screen is being discussed at 07:08 | Whether to hold or pull back — Layer 8 |

**The decision this layer owns:** *what each element means, and when each is the
subject.* Nothing about appearance, position, timing or motion.

### The three jobs

| # | Job | Why it cannot be done earlier |
|---|---|---|
| 1 | Resolve every `semantic_type` that Layer 3 left null | Needs the narration, which Layer 3 never sees |
| 2 | Build the **focus map** — which element is the subject, when | Needs both the elements and the timeline |
| 3 | Settle **entity identity** — which names denote one thing | Layer 3 explicitly refused: *"two names for one thing, and this layer does not decide whether they are the same"* |

**Job 2 is the one nothing else can do.** Layer 3 knows the slides. Layer 4 knows
the time. `slidechanges` knows which slide is on screen when. **Nothing knows
which element is the subject** — and Layer 8 cannot place a single beat without
it. On V017, slide 5 holds 519 words across 3 m 22 s and six elements; without a
focus map that is one undifferentiated window and the consumer code block sits
inert for two minutes.

---

## 2 · The prompt to run

**Four steps. Two are tools.**

| Step | How | Required? |
|---|---|---|
| **1** | `mpk video slidechanges --deck` — windows, slide identity, focus arrow | Yes |
| **2** | A prompt — meanings, focus map, entities | Yes |
| **3** | `mpk review build -t representation-review` — the review page | Yes |
| **4** | You confirm, in the same three-field review file | Yes |

---

### Step 1 — what is on screen, when

```
mpk video slidechanges res/workdir/V017.mp4 \
    --video-id v017 --deck "res/inputs/P17-OS-PS-Bounded Buffer Problem.pptx" \
    --deck-id v017 \
    -o res/workdir/v017.changes.json \
    --html res/workdir/v017.changes.html
```

Produces the window table the prompt binds against. **Confirm it by eye first** —
the page shows each window's video frame beside its matched deck slide.

**Windows may legitimately match no slide.** On V017, five of eight do not: the
intro cards, the title card, the presenter composition, and the two outro cards.
That is a finding, not an error, and the prompt must handle it rather than
forcing every window onto a slide.

#### The arrow is deliberately withheld from the prompt

`slidechanges` extracts `focus_ground_truth` — a hand-placed orange arrow marking
what is being discussed. **Do not attach it to the step-2 prompt.** A model given
the answer will reproduce it, and the run then proves nothing about whether the
prompt can find the answer itself.

It is used in **step 3**, by the tool, to check the focus map the prompt produced.
Disagreement is a measurable prompt defect rather than an argument.

---

### Step 2 — the prompt

```
INPUTS
  - context.md (standing project brief)
  - visual-grammar.md
  - v017.manifest.json      from Layer 3
  - v017.transcript.json    from Layer 4, human-confirmed
  - v017.changes.json       from `mpk video slidechanges --deck`
    ATTACH THE JSON WITHOUT ITS THUMBNAILS — they are base64 images and
    carry no information you can use.

Use only: VGR-01, VGR-05, VGR-07. Ignore all other requirement entries.
If a requirement outside that list appears relevant, name it and stop.

YOU ARE RUNNING LAYER 5 — SLIDE REPRESENTATION, over a whole video.
You decide what things MEAN. You decide nothing about how they look,
where they sit, or when they animate.

────────────────────────────────────────────────────────────────────
COVERAGE — do this first and report it
────────────────────────────────────────────────────────────────────
State three counts before anything else:
  - elements in the manifest
  - segments in the transcript
  - windows in the changes file, and how many carry a slide_id

Then confirm the windows and the manifest agree: every slide_id in the
windows must exist in the manifest, and every slide in the manifest must
either appear in a window or be named as absent.

On V017 two deck slides appear in NO window. That is expected and
explained — the video's title card is styled differently from the deck's,
and deck slide 2 is a reconstruction of a composition with the presenter
removed. Report it; do not treat it as an error and do not try to force
a match.

────────────────────────────────────────────────────────────────────
EVIDENCE — the rule that governs everything below
────────────────────────────────────────────────────────────────────
Every meaning you resolve MUST cite what was said: the quote, the
segment_id, and the timestamp. A resolution without a citation is a
guess wearing a decision's clothes.

If nothing in the narration bears on an element, its semantic_type stays
null and its status is "no_narration". That is a correct answer, not a
failure — an empty spacer box has nothing said about it because there is
nothing to say. Recording it proves it was considered rather than missed.

DEICTIC REFERENCE IS THE STRONGEST EVIDENCE. When he says "as we see
here", "this one", "over here", he is pointing at something on screen at
that moment. Prefer it over inference from wording.

────────────────────────────────────────────────────────────────────
JOB 1 — RESOLVE SEMANTIC TYPE
────────────────────────────────────────────────────────────────────
Layer 3 left every semantic_type null and recorded a
semantic_type_prior instead. Resolve each one against the narration in
the window where that slide is on screen.

USE THIS VOCABULARY. It is fixed (DEC-002).

  ENTITIES — things that exist
    process_actor   a process or thread that acts (producer, consumer,
                    reader, writer, Pi)
    resource        the thing acted on (buffer, shared file, Rj)
    counter         a number that GOES UP AND DOWN (empty, full, Available)
    capacity        a fixed size that does NOT change (BUFSIZE, n)
    lock            mutual exclusion (mutex)
    state_flag      a condition true or false (safe/unsafe, blocked)

  RELATIONS — one thing acting on another
    enqueue         data moves IN
    dequeue         data moves OUT
    request         an actor asks for a resource
    assignment      a resource is held by an actor
    access          an actor uses a resource without transfer

  CONTROL — points in a procedure
    wait_point      execution may block here
    signal_point    execution releases something here
    guard           a condition that decides a branch

  STRUCTURE — carries content, no domain meaning
    title  body_text  code_block  code_line  matrix  matrix_cell
    label  annotation  panel  list_item

  CHROME — superseded by the style contract
    background  footer_band  logo  slide_number

THE LIST CONSTRAINS MEANING, NOT FORM. Slide 3's connector and slide 5's
code line "next_produced ----> buffer" both mean data moving into the
buffer, and both resolve to `enqueue`. They will not LOOK alike — shape
comes from the element's own type, which Layer 3 already recorded. One
meaning, one binding in Layer 6, two different pictures.

To add a term, name it and state why no existing term fits. Do not add
one silently.

────────────────────────────────────────────────────────────────────
JOB 2 — THE FOCUS MAP
────────────────────────────────────────────────────────────────────
For every moment of the video, say which element is the subject.

  - Bind to element_ids. Where an element has lines[], bind to the LINE
    INDEX as well. VGR-05 requires word/phrase-level pacing, and Layer 8
    should not have to re-read the narration to find what you already
    read. On V017 slide 5 he walks wait(empty) -> wait(mutex) ->
    signal(full) inside 85 seconds; a window naming only the code block
    has thrown that away.
  - A window may have NO subject. "As an exercise we would like you to
    think about the following" points at nothing on screen. Record it
    with an empty subject and the role `exercise`. An empty subject is
    information — it tells Layer 8 to hold rather than hunt for
    something to animate.
  - Several elements may be the subject at once when he compares them.
  - Every focus window carries a role, from this fixed list:
        title_card  recap  motivation  walkthrough  worked_example
        summary  exercise  transition
  - `recap` matters most: he is summarising what came before, so NOTHING
    NEW should appear. Without the label, Layer 8 sees narration with no
    matching visual and invents something.

The focus windows must tile the video with no gaps and no overlaps.
Silence is a window too.

────────────────────────────────────────────────────────────────────
JOB 3 — ENTITY IDENTITY
────────────────────────────────────────────────────────────────────
Decide which names denote one thing. Layer 3 recorded candidates and
refused to merge them: "two names for one thing, and this layer does not
decide whether they are the same."

Merge only on narration evidence, and cite both sides. On V017: "The
buffer is of size, buff size" at 01:59, then "a shared buffer of size n
elements" at 02:35 — thirty-six seconds apart, same quantity, both
names. That is enough. Geometric or textual similarity alone is NOT.

Give each entity one canonical name from the vocabulary, list its
aliases and every element_id it appears as, across all slides.

────────────────────────────────────────────────────────────────────
WHAT YOU MUST NOT DO
────────────────────────────────────────────────────────────────────
DO NOT CORRECT THE DECK. v017_s05_104 reads "If  0, waits" with an
operator missing, against its mirror "If > 0, adds to buffer". The
narration supports "== 0". You may RECORD that as evidence for OBS-033.
You may NOT write the corrected text into any field. Guessing an
operator into an educational artifact is worse than showing one is
missing, and the deck is fixed in PowerPoint, not here.

DO NOT INVENT ELEMENTS. Every meaning must attach to an element_id that
exists in the manifest. If the narration describes something the slide
does not contain, say so under FLAGS — do not create it.

DO NOT DECIDE APPEARANCE, POSITION OR TIMING. No colours, no sizes, no
grid cells, no durations, no reveal order. Those belong to Layers 6
and 8, and a value invented here will be adopted and then defended.

────────────────────────────────────────────────────────────────────
OUTPUT — <video>.representation.json
────────────────────────────────────────────────────────────────────
{
  "video_id": "v017",
  "deck_id": "v017",
  "metadata": { inputs {manifest, transcript, windows}, layer, scope,
                counts {elements_resolved, elements_no_narration,
                        focus_windows, entities, vocabulary_terms_added} },
  "elements": [
    { element_id, slide, prior_from_layer3, semantic_type,
      status: "resolved" | "no_narration" | "unresolved",
      basis: { quote, segment, at } } ],
  "focus_map": [
    { start, end, slide, window_kind, subject: [element_id, ...],
      lines: [{element_id, line_index}], role, basis } ],
  "entities": [
    { canonical, aliases[], element_ids[], status, basis } ],
  "vocabulary_additions": [ { term, why_no_existing_term_fits } ],
  "unresolved": [ { what, why_unresolved, owner } ]
}

Every element in the manifest must appear exactly once in `elements`
(VGR-07). The focus windows must cover the full duration.

End with UNRESOLVED / ASSUMPTIONS / FLAGS. Write "none" if genuinely
empty.
```

---

### Step 3 — the review page and the checks

```
mpk review build res/workdir/v017.representation.json \
    -t representation-review -o res/workdir/v017.representation.html

mpk check representation res/workdir/v017.representation.json \
    --manifest res/workdir/v017.manifest.json \
    --transcript res/workdir/v017.transcript.json \
    --windows res/workdir/v017.changes.json
```

The check is where VGR-07 stops being a rule with no enforcement:

| Check | Fails when |
|---|---|
| element coverage | an element in the manifest appears zero or twice |
| focus coverage | the focus windows leave a gap or overlap |
| citation | a `resolved` element has no quote, segment or timestamp |
| vocabulary | a term outside the fixed list arrives without a stated reason |
| slide agreement | a focus window names a slide that is not on screen then |
| **arrow agreement** | the focus map disagrees with `focus_ground_truth` |

**The arrow check is the interesting one.** It compares the prompt's focus map
against the hand-placed arrow extracted in step 1 — `x` gives the column, `y`
gives roughly the line. It covers 28.6% of deck-slide time on V017, so it can
**confirm a wrong answer but never produce a right one**. Disagreement is
reported, never auto-corrected.

**Both exist.** The check found nine failures in this layer file's own worked
example — seven ad-hoc vocabulary terms written before DEC-002 fixed the list, a
97.75 s hole in the focus map, and 37 unaccounted elements. A check that passes
the first thing you point it at has not been tested.

---

### Step 4 — you confirm

Same three-field format as Layers 4 and 5's window review, so it is one habit:

```
MM:SS | fix   | v017_s03_84 is dequeue, not enqueue
04:13 | check | is the producer block really the subject this whole time?
01:59 | ok    | BUFSIZE = n confirmed
all   | ok    | reviewed every element
```

---

## 3 · What it emits

| Form | What | For |
|---|---|---|
| **Build from** | `<video>.representation.json` | Layers 6 and 8 |
| **Decide with** | `<video>.representation.html` | You |

### Required — frozen

| Field | Read by | Why it cannot be omitted |
|---|---|---|
| `elements[].semantic_type` | 6, 8 | The whole point of the layer |
| `elements[].basis` | review; audit | A resolution without evidence is a guess |
| `elements[].status` | the coverage check | `no_narration` is an answer, not a gap |
| **`focus_map[]`** | **8** | Nothing else says which element is the subject when |
| `focus_map[].role` | 8 | `recap` means nothing new may appear |
| `focus_map[].lines` | 8 | VGR-05 — word/phrase pacing needs line granularity |
| `entities[]` | 6 | One entity, one binding, one colour |

### Observed — open

`vocabulary_additions`, `unresolved`, window kinds, per-element confidence notes.
Append freely.

---

## 4 · Review before proceeding

| # | Check |
|---|---|
| 1 | Does every element appear exactly once? |
| 2 | Does every `resolved` element cite a quote, a segment and a time? |
| 3 | Do the focus windows tile the video with no gaps? |
| 4 | Is every `recap` window genuinely a recap? Getting this wrong means new content appears during a summary |
| 5 | Are the entity merges justified by narration on **both** sides, not by similar text? |
| 6 | Did any vocabulary term get added, and is the reason honest? |
| 7 | Does the focus map agree with the arrow where the arrow exists? |
| 8 | Was the deck left uncorrected — is `v017_s05_104` still wrong everywhere? |
| 9 | Are there any colours, sizes, positions or durations in the output? There must be none |
| 10 | Do the windows with no slide_id have sensible roles rather than being forced onto a slide? |

---

## 5 · Verification status

| | |
|---|---|
| `mpk video slidechanges --deck` | ✅ run on V017: 8 windows, 3 matched at 0.996, 20 focus runs. Confirmed by eye |
| **The step-2 prompt** | ⚠ **never run.** The first real run is the test — expect to fix something |
| `mpk check representation` | ✅ built. Six checks: element coverage, citation, vocabulary, focus tiling, slide agreement, arrow agreement |
| `representation-review` template | ✅ built. Surfaces missing citations and focus-map holes at the top, before the tables |

---

## Changelog

- **v1.1** — `capacity` split out of `counter`. The first real run resolved
  V017's `BUFSIZE` label as `counter`, correctly following the definition — which
  read *"a number that changes (empty, full, **n**, Available)"* and listed the one
  quantity in the set that never changes. `empty` and `full` go up and down;
  `BUFSIZE` and `n` are fixed. Conflating them would have had Layer 6 animate a
  constant. A defect in the vocabulary, not in the prompt that obeyed it.

- **v1** — written after the Layer 5 / Layer 6 boundary was settled. Layout moved
  out to Layer 6, because choosing a Direction needs the meanings while the
  meanings do not need the Direction. The focus map was added as a first-class
  output once slide 5 showed 519 words over six elements with nothing saying which
  was the subject. The vocabulary is fixed per DEC-002, constraining meaning and
  not form. The focus arrow is deliberately withheld from the prompt and used only
  to check it — a model handed the answer reproduces it and the run proves nothing.
  Three prohibitions are stated explicitly because each has already been violated
  once in this project: do not correct the deck (OBS-033), do not invent elements
  (PROP-003), do not decide appearance.
