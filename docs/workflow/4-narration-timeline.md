# Layer 4 — Narration Timeline

**Scope:** per video · **Prompt version:** v1.2 · **Work status:** tools run on V017; step-3 prompt not yet verified in a fresh chat
**Emits:** `<video>.transcript.json` (build from) + `<video>.transcript.html` (decide with)
**Tooling:** `mpk audio extract` · `mpk audio asr` · `mpk transcript build` · `mpk transcript reflag` · `mpk transcript export`

> **Maps to the `Transcript Alignment` module.** That name is the owner in four
> register rows (TGT-006, TGT-007, TGT-011, RC-003) and in DEC-001. Those
> citations still resolve — this layer is the manual pass that module will
> replace.

---

## 1 · What it does

Produces **what was said, and exactly when.** Facts only.

**The decision this layer owns:** none about content. The narration is fixed by
the project invariant. What this layer owns is **the time axis** — and it is the
only layer that creates one. Every timestamp in Layer 8's beat sheet traces back
to a number produced here.

| This layer answers | This layer does **not** answer |
|---|---|
| The word "requests" begins at 13.55 s and ends at 13.80 s | Which visual should appear then |
| There is a 2.3 s silence at 04:12 | Whether that silence is a defect |
| The recogniser heard "P I", confidence 0.42 | Whether the slide's `P₁` node is what he meant |

**Why "timeline" and not "transcript".** A transcript is a document; the
artifact here is a time axis with words attached to it. Silence is part of it —
a transcript has no way to record a pause, and TGT-011 (duration matches the
full narration) needs one.

**Runs in parallel with Layer 3.** They share no inputs: Layer 3 reads the deck,
Layer 4 reads the audio. Neither blocks the other.

### The five jobs

| # | Job | Who does it |
|---|---|---|
| 1 | Extract audio on **two separate paths** — 48 kHz stereo master, 16 kHz mono for recognition | tool (RC-003) |
| 2 | Transcribe — speech to words, verbatim | tool |
| 3 | **Force-align** — every word gets a start and an end | tool (DEC-001) |
| 4 | Verify the segmentation is usable by Layer 8 | prompt |
| 5 | **Propose notation corrections** from the text and the deck's labels — a human confirms by ear | prompt + human (OBS-021) |

**This is the first layer where the tool does most of the work and the prompt is
a reviewer rather than a producer.** Jobs 1–3 are fully deterministic. The
prompt's value is jobs 4 and 5, and pretending otherwise would mean padding a
generation prompt that has nothing to generate.

### What "verbatim" does and does not mean

| | |
|---|---|
| **Must not change** | The audio, the timings, the words the professor actually said. Do not clean up, summarise, reorder, or tidy grammar |
| **Must be corrected** | A **mis-transcription**. If he said `Pᵢ` and the recogniser wrote "pie", the transcript is wrong and fixing it makes the record accurate |

The invariant protects the *narration*, not the recogniser's guess about it.
Correcting a transcription error is not a change to the narration — it is the
removal of an error we introduced.

---

## 2 · The prompt to run

**Four steps. Three are tools; the prompt is step 3.**

| Step | How | Required? |
|---|---|---|
| **1** | `mpk audio extract` + `mpk audio asr` — the two audio paths | Yes |
| **2** | `mpk transcript build` — transcribe + align → raw ASR JSON | **Default** |
| **2-alt** | A session with **local access** runs the same steps itself | Option |
| **3** | A prompt — verify segmentation, confirm notation → final transcript | Always |
| **4A** | `mpk transcript export` — build the review page | **Default** |
| **4B** | The prompt fills the template itself | Option |
| **5** | **You listen**, write a review file, `mpk transcript apply` → the artifact | Yes |

---

### Step 1 — the two audio paths

```
mpk audio extract V017.mp4 -o res/workdir/V017-master.wav   # 48 kHz stereo
mpk audio asr     V017.mp4 -o res/workdir/V017-asr.wav      # 16 kHz mono
```

Two commands, two files, deliberately. **RC-003** exists because our previous
output shipped the 16 kHz mono recognition copy as the delivered audio. One
command with a flag would make that mistake possible again; two commands make it
hard.

Recognition uses the 16 kHz copy. Delivery uses the 48 kHz master. They never
meet.

---

### Step 2 — transcribe and align

```
mpk transcript build res/workdir/V017-asr.wav \
    --video-id v017 --model small \
    --terms-from res/workdir/v017.manifest.json \
    --vocab "semaphore, mutex, wait, signal, critical section" \
    -o res/workdir/v017.asr.json
```

Emits **raw ASR output** — the same relationship `mpk deck extract` has to
Layer 3's prompt. `word_timestamps` is always on: DEC-001 makes word timings
mandatory, and a segment without them is one Layer 8 cannot bind a beat inside.

**Bias the vocabulary — this is the cheapest fix for OBS-021.** Notation is
where recognition fails, and biasing the recogniser *before* it runs beats
detecting the error afterwards.

> **Layer 3's `entity_inventory` is the vocabulary list.** It already holds every
> labelled shape in the deck — Producer, Consumer, BUFSIZE, P1, R1 — which is
> exactly the terminology the narration uses. When Layer 3 has run for a video,
> feed its manifest in via `--terms-from`. This is the one place the two
> parallel branches usefully touch.

**`--terms-from` is necessary but not sufficient (OBS-032).** The deck carries
only what is *written on a slide*. V017's manifest yields three terms — BUFSIZE,
`next_produced`, `next_consumed` — while the narration leans on *semaphore*,
*mutex*, *wait*, *signal*, which are spoken and never drawn. So the critical-term
list is the **union** of `--terms-from` and `--vocab`: deck labels plus the
spoken vocabulary of the topic. On V017 that union is 14 terms and flags 38 of
64 segments; the deck alone flagged 0.

Matching is deliberately tolerant, because a recogniser mangles an identifier in
ways you cannot predict: the deck says `BUFSIZE`, the recogniser wrote
*"buff size"* — split in a different place, with a doubled letter. The matcher
allows a separator between any two characters and allows any character to
repeat. False positives cost a row in the review page; a miss costs a wrong
symbol on screen.

**To re-flag without re-transcribing**, which takes seconds instead of minutes:

```
mpk transcript reflag res/workdir/v017.asr.json \
    --terms-from res/workdir/v017.manifest.json \
    --terms "semaphore, mutex, wait, signal"
```

Use this when Layer 3 has since run, or when the review page shows a term the
list missed. It rewrites the flags in place and prints the before/after count.

What the command also records, because they are facts and nothing else measures
them: per-word confidence, **pauses at or above `--pause`** (default 1.0 s),
`no_speech_prob` per segment, and a flag on every segment containing notation.

**Segments stay as the recogniser produced them.** Re-segmenting on clause
boundaries would be a *decision*, and this is a facts layer. Layer 8 sub-selects
word spans from `words[]`, so it never needs a segment to match a clause.

#### Step 2-alt — a session with local access

Instead of running the commands yourself, a session with local access can run
them. It needs:

| Access | For |
|---|---|
| Read the source video | `mpk audio extract` / `asr` |
| Write to a working directory | the two audio files and the JSON |
| Run `ffmpeg` / `ffprobe` | audio extraction |
| Run `mpk` (so `python-pptx`, `faster-whisper` installed) | transcription |
| Network on first run **only** | the Whisper model downloads once from Hugging Face. On a blocked network, fetch it once elsewhere and pass `--model-dir` |

The outputs are identical either way. The default is the tool path because it is
reproducible and leaves a command in the capture log; local access is for when
you would rather not shuttle files.

---

### Step 3 — verify (the prompt)

```
INPUTS
  - context.md (standing project brief)
  - visual-grammar.md
  - v<video>.asr.json from `mpk transcript build`
  - v<deck>.manifest.json from Layer 3, if it exists — its entity_inventory
    is the strongest evidence available for notation corrections

Use only: VGR-01, VGR-05. Ignore all other requirement entries. If a
requirement outside that list appears relevant, name it and stop.

YOU ARE RUNNING LAYER 4 — NARRATION TIMELINE, verification pass.
You are NOT transcribing. The words and their timings already exist. Your
job is to say whether they are trustworthy, and to correct transcription
errors — never to improve the professor's phrasing.

────────────────────────────────────────────────────────────────────
WHAT YOU MUST NOT DO
────────────────────────────────────────────────────────────────────
Do not clean up grammar, remove filler, merge sentences, reorder, or
summarise. The narration is fixed by the project invariant. A transcript
that reads better than the lecture is a corrupted record.
Do not change any timing. A correction changes a token, never its clock.

────────────────────────────────────────────────────────────────────
NOTATION — PROPOSE, DO NOT CONFIRM
────────────────────────────────────────────────────────────────────
YOU CANNOT HEAR THE AUDIO. Do not claim to. Your job is to propose
corrections with evidence; a human confirms them by ear in the review
page, where clicking a word plays just that word's span.

For every segment flagged notation_present, examine the text and propose
a correction where the recogniser has plainly mangled a symbol —
"P sub i", "P one", "pie", "are two", "P I" and similar.

USE THE DECK AS EVIDENCE. If the Layer 3 manifest is attached, its
entity_inventory lists every labelled shape in the deck: Producer,
Consumer, BUFSIZE, P1, R1. When the narration is discussing a slide whose
nodes are labelled P1 and R1, "pie" is almost certainly "P1". Cite the
element you are reasoning from. This is evidence you can actually check,
unlike the audio.

Record a proposal, never a silent overwrite:

    "text": "from P sub i to R sub j",
    "text_proposed": "from Pi to Rj",
    "corrections": [
      {"from": "P sub i", "to": "Pi", "word_indices": [2, 3, 4],
       "basis": "recogniser wrote 'P sub i'; the deck labels this node P1
                 (v017_s03_10)",
       "status": "proposed",
       "confirmed_by": null}
    ]

status is ALWAYS "proposed". Only the human sets it to "confirmed" and
fills confirmed_by, after listening. A correction you cannot justify from
the text or the deck must be left alone and raised in FLAGS instead.

WHEN A CORRECTION MERGES TOKENS, the merged token spans from the FIRST
token's start to the LAST token's end. Never invent an interior boundary.
Three tokens becoming one means one word span, not three.

WHY THIS PASS EXISTS. Mis-transcribed notation is invisible to an overall
word-error rate, because the errors cluster in exactly the segments that
carry meaning. A beat bound to "Rj" that fires on the wrong word is a sync
defect whose cause is two layers upstream, and it will be hunted at
Layer 8 where it cannot be found.

────────────────────────────────────────────────────────────────────
SEGMENTATION — IS IT USABLE?
────────────────────────────────────────────────────────────────────
Do not re-segment. Report instead:
  - segments with no word timings — Layer 8 cannot bind inside them
  - segments that overlap
  - a segment so long it spans several distinct ideas: name the ideas and
    the approximate word index where each starts, so Layer 8 knows a
    sub-selection is available
  - words whose confidence is low enough to doubt

────────────────────────────────────────────────────────────────────
PAUSES
────────────────────────────────────────────────────────────────────
Report every gap the tool flagged, with its duration. Say which read as
natural breath and which as dead air — but only as an observation. The
dead-air threshold is not set (OBS-007), and whether a pause is a defect
is Layer 8's decision, not yours.

────────────────────────────────────────────────────────────────────
OUTPUT — THE FINAL TRANSCRIPT
────────────────────────────────────────────────────────────────────
Emit the ASR JSON with your additions merged in. Keep every field it
already has. Add per segment where applicable:
    text_corrected, corrections[], flags[] (appended, not replaced),
    ideas[] for over-long segments
And at metadata level:
    verified: true, notation_segments_examined: <n>,
    corrections_proposed: <n>, corrections_confirmed: 0,
    verification_note: "<what you could not judge from text or deck>"

Set metadata.extraction_path to "mpk_transcript_build+verified".

End with UNRESOLVED / ASSUMPTIONS / FLAGS. Write "none" if genuinely
empty.
```

---

### Step 4 — the review page

**4A (default):**

```
mpk transcript export v017.transcript.json -f html \
    --audio res/workdir/V017-asr.wav -o v017.transcript.html
```

Two columns — **time \| text** — with the audio embedded, so:

| Interaction | Why it matters |
|---|---|
| **Click a timestamp** → plays from there | Reading a transcript tells you nothing about sync |
| **Click a word** → plays *just that word's span* | This is what makes the notation check take seconds instead of minutes |
| Word highlights as it plays | You see the alignment, rather than trusting it |
| **Notation segments only** filter | A 17-minute transcript becomes a 2-minute check |
| Pauses shown as gaps, with durations | Silence is visible instead of implied |

The audio is embedded as a `data:` URI, so the page is one self-contained file
you can keep or send. A 17-minute mono recording adds roughly 11 MB.

**4B:** the prompt emits `transcript-review.html` verbatim with the transcript
substituted into its `<script id="transcript">` block, and the audio into
`<script id="audio-data">`. Same template, same page.

**Do not hand-write table rows, on either path.** The page renders from the
embedded transcript, which is what stops the table and the data from disagreeing.

Other formats, all derived from the same JSON:

```
mpk transcript export v017.transcript.json -f txt  -o v017.transcript.txt
mpk transcript export v017.transcript.json -f vtt  -o v017.vtt
```

| Format | Consumer |
|---|---|
| `txt` | Stamped, paste-able — for the professor to read or correct by hand |
| `vtt` | WebVTT. Layer 8's player loads it as a `<track>` for the caption bar |

---

### Step 5 — listen, decide, apply

Step 3 emits **proposals**. Nothing is true until someone has heard it. This is
the step that turns proposals into the artifact.

**You write a review file while listening.** One line, three fields, so it is
typeable at speed:

```
MM:SS | kind | comment
```

| kind | means |
|---|---|
| `fix` | the words are wrong — `heard -> should be` |
| `check` | needs a second look; **states what to look at** |
| `ok` | listened, correct as transcribed |
| `ask` | cannot decide; needs someone else |
| `skim` | deliberately not listened to — a stated gap, not a verdict |

`all` in the time column applies to the whole transcript, and the `all` line is
how coverage gets recorded. **`skim` is not a lesser `ok`.** One says we checked
and were satisfied; the other says we never looked. When a wrong symbol reaches
the screen and someone asks whether it was checked, the file has to answer
truthfully.

```
mpk transcript apply res/workdir/v017.asr.json \
    --review res/workdir/v017.review.txt \
    --by "Akshat" \
    -o res/workdir/v017.transcript.json
```

**What it guarantees.** Timings are never invented. A correction spans exactly
the first replaced token's start to the last one's end — no interior boundary is
created, because the audio did not change, only our label for it. Where one word
becomes several the new words split the span evenly; that *is* a guess and every
such word carries `timing_estimated: true`. Trailing punctuation is carried
across, since sentence boundaries are what Layer 8 reads to find where an idea
ends.

**What it refuses to do.** It does not resolve `check` and `ask` lines — those
become `open_question_*` flags on the segment and travel to Layer 8, which is the
first layer that can answer them. A review comment that silently vanishes is
worse than one never written. It also fails loudly when a line cannot be applied
rather than writing a partial artifact; `--keep-going` overrides that, on purpose
requiring a decision.

Matching is tolerant of tokenisation. A reviewer writes what they *read*
("water-independent"); the recogniser may hold two tokens (`water`,
`-independent`), and the clock read off a player can land in the neighbouring
segment. A review file you can only write if you know the tokenisation is a
review file nobody can write, so the tool matches letters-and-digits only, glued
across token boundaries, and looks two segments either side.

After applying, re-flag notation on the corrected text — the words changed, so
the flags should:

```
mpk transcript reflag res/workdir/v017.transcript.json \
    --terms-from res/workdir/v017.manifest.json -o res/workdir/v017.transcript.json
mpk transcript check res/workdir/v017.transcript.json
```

**The V017 run:** 8 corrections applied, 3 open questions carried, 0 failures,
1056 words, 49 of 64 segments notation-bearing, `check` clean.

---

## 3 · What it emits

| Form | What | For |
|---|---|---|
| **Build from** | `<video>.transcript.json` | Layers 5 and 8; `Transcript Alignment` fixtures |
| **Decide with** | `<video>.transcript.html` | You, confirming notation and sync by ear |
| Derived | `.txt`, `.vtt` | Human reading; caption track |

### Required — frozen

| Field | Read by | Why it cannot be omitted |
|---|---|---|
| `segments[].segment_id` | 5, 8 | Every `narration_ref` names it |
| `segments[].start` / `end` | 5, 8 | Segment-level binding |
| **`segments[].words[]`** with `start` / `end` | **8** | VGR-05. Without it there is no word-level pacing and the layer has failed |
| `text` (and `text_corrected` where present) | 5, 8 | Matching narration to elements |
| `words[].probability` | 4's own review | Which words to doubt |
| `metadata.duration_s` | TGT-011 | The video must span it |
| `metadata.pauses_over_threshold` | 8 | Dead-air candidates |
| `flags[]` | 8; the review page | What needs a human |

### Observed — open

`avg_logprob`, `no_speech_prob`, `language_probability`, `vocab_bias`,
`corrections[]`, `ideas[]`, model and compute settings. Append freely.

---

## 4 · Review before proceeding

| # | Check |
|---|---|
| 1 | Does every segment carry `words[]` with start and end? |
| 2 | Does `metadata.duration_s` match the source video? A short transcript means a truncated read |
| 3 | Was the 48 kHz master kept separate from the 16 kHz recognition copy (RC-003)? |
| 4 | Was **every** `notation_present` segment examined — not sampled? |
| 5 | Is every correction `status: "proposed"` with its basis and the original text preserved? |
| 5a | Have **you** confirmed each proposal by ear in the review page, and set `confirmed_by`? The model cannot hear; only this step closes the loop |
| 6 | Where a correction merged tokens, does the merged span run first-start to last-end? |
| 7 | Has any timing been altered? It must not have been |
| 8 | Does the text read like the lecture rather than like prose? Tidied grammar means the record was corrupted |
| 9 | Do any segments overlap, or run backwards? |
| 10 | Was word-error rate measured against a reference sample (`jiwer`, already a dependency)? Advisory ≤ 12% |
| 11 | Does the review page open, play, and highlight words in step with the audio? |
| 12 | Is the embedded transcript identical to the JSON artifact? |

Check 4 is the one that will be tempting to sample. Don't — the value is
entirely in the segments that carry notation, and there are few of them once the
filter is on.

### What the next layers need

| Layer | Needs |
|---|---|
| **5** Representation | Segment text and ids, to resolve `semantic_type` from what the narration says |
| **8** Sequence | `words[]` — it selects the word span for each beat and derives start and duration from it. **This is the whole reason word timings are mandatory** |
| **7** Audio | Nothing. Parallel branch; mastering does not need to know what was said |

---

## Verification status — honest

| | |
|---|---|
| `mpk transcript export` (all four formats) | ✅ tested against a realistic 6-segment, 137-word transcript |
| `transcript-review.html` | ✅ rendered headlessly — 137 word spans, 4 notation rows, flags, embedded audio |
| `mpk transcript check` | ✅ tested |
| **`mpk transcript build`** | ✅ **run on V017**: 64 segments, word timings present, `small` model. It did fail on first run — notation detection reported 0 of 64 — and that is fixed (OBS-032). OBS-030 closed |

---

## Changelog

- **v1.2** — first real run on V017 exposed a defect the code review missed:
  notation detection was a hardcoded regex for one deck's vocabulary, and
  reported **0 of 64** segments on a transcript full of *semaphore* and *mutex*.
  Step 2 now drives detection from Layer 3's manifest via `--terms-from`,
  unioned with `--vocab` — the deck alone is not enough, because the spoken
  vocabulary of a topic is larger than what any slide draws. `mpk transcript
  reflag` added so the list can be corrected without re-transcribing. OBS-032
  logged and closed; OBS-030 closed.

- **v1.1** — corrected a false assumption: the step-3 prompt told the model to
  confirm notation *by ear*, which it cannot do — audio cannot be attached to a
  chat. Corrections are now `status: "proposed"`, justified from the text and
  from Layer 3's `entity_inventory`, and only a human sets `confirmed_by` after
  listening in the review page. Found while preparing the prompt for its first
  fresh-chat run.

- **v1** — written before the first run. Structure mirrors Layer 3: tool
  produces raw output, prompt verifies and produces the artifact, tool or prompt
  builds the review page. Named "narration timeline" rather than "transcript"
  because the artifact is a time axis and silence is part of it. Vocabulary bias
  linked to Layer 3's `entity_inventory` — acting on OBS-021 at the source
  instead of only detecting it. Segmentation deliberately left as the recogniser
  produced it, since re-segmenting would be a decision in a facts layer.
