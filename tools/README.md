# tools/

**`mpk` — Media Pipeline Kit.** Command-line utilities for the Lecture Alive AI
workflow.

The division of labour: **deterministic work lives here, judgement lives in the
layer prompts.** A prompt should never do arithmetic that a file already
contains — geometry, text, indent levels and connector endpoints are all
explicit in a `.pptx`, and reading them from a rendered picture converts known
values into guesses.

```
tools/
  mpk                           launcher — ./tools/mpk works with no install
  mpk.py                        the tool
  templates/
    slide-review.html           Layer 3 — deck manifest review
    transcript-review.html      Layer 4 — narration timeline review
  README.md                     this file
```

---

## Install

Nothing to install for the tool itself — it is one file. Run it directly:

```bash
./tools/mpk --help              # the launcher
python3 tools/mpk.py --help     # or call Python yourself
```

**For a bare `mpk` from any directory**, pick one:

```bash
# add tools/ to PATH — put this in ~/.bashrc
export PATH="$PATH:/path/to/media-pipeline/tools"

# or alias it
alias mpk='python3 /path/to/media-pipeline/tools/mpk.py'
```

**Not** a `[project.scripts]` entry. This project builds with hatchling and
ships only `src/pipeline`; adding `mpk = "tools.mpk:main"` would require
installing a top-level package literally called `tools`, which is too generic a
name to put on anyone's import path. The launcher costs nothing and avoids that.

### Full install, from a fresh clone

```bash
cd /path/to/media-pipeline

# 1 · Python dependencies — all declared in pyproject.toml
pip install -e .
#     python-pptx, faster-whisper, ffmpeg-python, jiwer, pydantic, typer…

# 2 · System programs the tool shells out to
sudo apt install ffmpeg libreoffice poppler-utils
#     ffmpeg / ffprobe  -> audio and video commands
#     libreoffice       -> mpk deck render
#     poppler-utils     -> pdftoppm, the PDF -> PNG half of deck render

# 3 · Make the launcher executable
chmod +x tools/mpk

# 4 · Verify
./tools/mpk --version
python3 -c "import pptx, faster_whisper; print('python deps ok')"
for c in ffmpeg ffprobe soffice pdftoppm; do command -v $c >/dev/null || echo "MISSING: $c"; done
```

**First `transcript build` downloads a Whisper model** (~480 MB for `small`,
~75 MB for `tiny`) into `~/.cache/huggingface`. The
*"unauthenticated requests to the HF Hub"* warning is normal — the download
proceeds anonymously; a `HF_TOKEN` only raises rate limits. Later runs use the
cache and need no network.

### External programs

| Program | Needed by | If missing |
|---|---|---|
| `python-pptx` | every `deck` command | hard error |
| LibreOffice (`soffice`) | `deck render` | that command only |
| `pdftoppm` (poppler-utils) | `deck render` → PNG | stops at PDF |
| `ffmpeg` / `ffprobe` | all `audio` and `video` commands | those commands only |
| `faster-whisper` | `transcript build` | hard error. Models download from Hugging Face on first use |

Each command checks for what it needs and says so plainly rather than failing
halfway through.

---

## Help

`-h` works at every level, so you never have to read this file to find a flag:

```bash
mpk --help                  # the six groups
mpk deck --help             # commands in a group
mpk deck extract --help     # flags for one command
mpk --version
```

---

## Commands

| Group | Command | What it does |
|---|---|---|
| **deck** | `info` | One line per slide: shape counts, canvas size, title |
| | `extract` | OOXML shape tree → JSON. **Layer 3 step 1** |
| | `normalize` | Rescale a deck to another canvas size |
| | `merge` | Splice slides from one deck into another, at a position |
| | `render` | Slides → PNG, via LibreOffice |
| **review** | `templates` | List available review templates |
| | `build` | Inject a manifest into a template → self-contained HTML. **Layer 3 step 3A** |
| **transcript** | `build` | Audio → raw ASR JSON with word timings. **Layer 4 step 2** |
| | `reflag` | Re-apply notation detection without re-transcribing |
| | `export` | → `json` / `html` / `vtt` / `txt`. **Layer 4 step 4A** |
| | `apply` | Apply a human review file → the final transcript. **Layer 4 step 5** |
| | `check` | Validate a transcript's timings |
| **audio** | `extract` | Video → 48 kHz stereo master |
| | `asr` | Video → 16 kHz mono copy for forced alignment |
| | `probe` | Format and loudness measurements. **Layer 7 input** |
| **video** | `probe` | Resolution, fps, codec, bitrate. **TGT-001…008** |
| | `uniquefps` | Unique frames per second. **TGT-013** |
| **check** | `manifest` | Validate a Layer 3 manifest against the layer's rules |

Every command that produces a reviewable artifact has a matching `check`:
`mpk check manifest` for Layer 3, `mpk transcript check` for Layer 4.

---

## Recipes

### Layer 3 — deconstruct a deck

```bash
# 1 · see what you have
mpk deck info res/inputs/V017-bounded-buffer.pptx

# 2 · extract the shape tree (step 1)
mpk deck extract res/inputs/V017-bounded-buffer.pptx \
    --deck-id v017 --expect 5 -o res/workdir/v017.raw.json

# 3 · run the Layer 3 prompt with that JSON attached (step 2)
#     -> produces v017.manifest.json

# 4 · build the review page (step 3A)
mpk review build res/workdir/v017.manifest.json \
    -o res/workdir/v017.review.html

# 5 · sanity-check the manifest
mpk check manifest res/workdir/v017.manifest.json
```

`--expect 5` warns if the slide count differs. Without it, a truncated read is
silent.

### Repair a deck before extracting

A slide reconstructed from a video frame usually arrives at the wrong canvas
size. Merging it as-is puts every coordinate in a different reference frame.

```bash
mpk deck info missing-slide.pptx          # confirm the mismatch

mpk deck normalize missing-slide.pptx \
    --like V017.pptx -o missing-fixed.pptx

mpk deck merge missing-fixed.pptx \
    --into V017.pptx --at 2 -o V017-full.pptx

mpk deck render V017-full.pptx -d render  # then look at it
```

**Always render after a merge.** A raw shape-tree copy does not re-link image
or theme parts, so a source slide containing pictures would lose them silently.
The command prints this warning; the render is how you confirm.

### Layer 4 — build a narration timeline

```bash
# 1 · two audio paths, deliberately two commands (RC-003)
mpk audio extract V017.mp4 -o res/workdir/V017-master.wav   # 48 kHz stereo
mpk audio asr     V017.mp4 -o res/workdir/V017-asr.wav      # 16 kHz mono

# 2 · transcribe + force-align. Bias the vocabulary: notation is where
#     recognition fails, and Layer 3's entity_inventory is the term list
mpk transcript build res/workdir/V017-asr.wav \
    --video-id v017 --model small \
    --vocab "P1, P2, Pi, R1, R2, Rj, semaphore, BUFSIZE" \
    -o res/workdir/v017.asr.json

# 3 · run the Layer 4 verification prompt -> v017.transcript.json

# 4 · review page, with the audio embedded so you can hear each word
mpk transcript export res/workdir/v017.transcript.json -f html \
    --audio res/workdir/V017-asr.wav -o res/workdir/v017.transcript.html

# other formats, all from the same JSON
mpk transcript export res/workdir/v017.transcript.json -f txt -o v017.txt
mpk transcript export res/workdir/v017.transcript.json -f vtt -o v017.vtt

# 5 · listen in the review page, write your verdicts, apply them
mpk transcript apply res/workdir/v017.asr.json \
    --review res/workdir/v017.review.txt \
    --by "Akshat" \
    -o res/workdir/v017.transcript.json

# the words changed, so re-flag notation, then validate
mpk transcript reflag res/workdir/v017.transcript.json \
    --terms-from res/workdir/v017.manifest.json -o res/workdir/v017.transcript.json
mpk transcript check res/workdir/v017.transcript.json
```

### The review file

Typed by hand while listening, so it has to be typeable: `MM:SS | kind | comment`.

```
00:21 | fix   | water-independent -> what are independent
01:20 | check | pause of 4-5 secs. Check if there is a slide change here?
01:59 | ok    | buff size — no change here. Meaning is different here
06:28 | fix   | sum of 4 -> semaphore
05:53 | ask   | "buffer" appears twice — speaker restarting, or recogniser doubling?
all   | ok    | listened to every segment; all others are correct as transcribed
```

Five kinds: `fix` (`heard -> should be`), `check`, `ok`, `ask`, `skim`. `all` in
the time column sets coverage.

**`skim` is not a lesser `ok`.** One says we checked and were satisfied, the
other says we never looked. That distinction is the file's whole value when
something goes wrong later.

`apply` never invents a timing: a correction spans exactly the first replaced
token's start to the last one's end. Where one word becomes several, the split is
even and every such word is marked `timing_estimated`. `check` and `ask` lines are
**not resolved** — they become `open_question_*` flags and travel to Layer 8, the
first layer that can answer them. A line that cannot be applied fails the run
rather than producing a partial artifact.

Matching is tolerant of tokenisation, because a reviewer writes what they read
("water-independent") while the recogniser may hold two tokens, and a clock read
off a player can land in the neighbouring segment.

The review page is how the notation check gets done: tick **notation segments
only**, then click each symbol to play *just that word's span*. You hear what was
said and read what the recogniser wrote. A word-error rate cannot catch this —
the errors cluster in exactly the segments that carry meaning.

Models download from Hugging Face on first use. On a blocked network, fetch one
elsewhere and pass `--model-dir`, or give `--model` a local path.

### Audio — the two paths must stay separate

```bash
mpk audio extract V017.mp4 -o V017-master.wav   # 48 kHz stereo — delivery
mpk audio asr     V017.mp4 -o V017-asr.wav      # 16 kHz mono   — alignment
mpk audio probe   V017.mp4                      # Layer 7 measurements
```

Per **RC-003**, the 16 kHz speech-recognition copy must never become the
delivery master. Our previous output shipped mono 16 kHz audio for exactly that
reason. Two commands, two files, no chance of confusing them.

### Video — check what the file actually shows

```bash
mpk video probe     out.mp4      # what the container declares
mpk video uniquefps out.mp4      # what the picture actually does
```

`probe` reads declared fps. `uniquefps` counts non-duplicate frames with
`mpdecimate`. A 30 fps file made of 8 unique frames per second reports 30 and
passes TGT-002 while still looking choppy — because encoding cannot add motion
that was never rendered (**RC-001**). That gap is why **TGT-013** exists.

Note: TGT-013 is defined over *active beat windows*, so deliberately still
content is not penalised. This command measures the whole file, which is a
floor rather than the gate itself.

---

## Templates

Review pages live in `templates/`. Each is a **complete HTML page whose embedded
JavaScript renders the data**; `mpk review build` only substitutes the data
block. One implementation per page, shared by the tool and by the layer prompt,
so the table and the JSON cannot drift apart.

```bash
mpk review templates                                   # what exists
mpk review build m.json -o out.html                    # default: slide-review
mpk review build m.json -t slide-review -o out.html    # by name
mpk review build m.json -t ./my-page.html -o out.html  # by path
```

To change what a review page shows, **change the data, not the markup.** If a
fact should be visible, it belongs in the manifest — as a flag, a prior, or a
deck-level field.

Planned, as their layers are written: `vocabulary-review` (Layer 6) and
`sequence-player` (Layer 8 — the beat sheet with transport, caption bar and
speed control). Each will be a template filled with data, never a new renderer.

`transcript-review` embeds the audio as a `data:` URI, so the page is one
self-contained file: click a timestamp to play from there, click a word to play
just that word's span. A 17-minute mono recording adds roughly 11 MB.

---

## What `deck extract` captures

Worth knowing, because two of these are easy to lose.

| | |
|---|---|
| `<p:sp>` `<p:pic>` `<p:cxnSp>` | shapes, pictures, connectors |
| `<p:graphicFrame>` | **tables** — a walk that only handles `<p:sp>` misses every matrix in a deck |
| `<p:grpSp>` | groups, descended into, with `parent_id` and both raw and resolved boxes |
| `lines[]` | **visual lines, not paragraphs** — see below |
| connector endpoints | from `a:stCxn` / `a:endCxn`, with the arrowhead end from `a:tailEnd` |
| `id_coverage` | which shape ids were captured, and any gaps |
| `flags[]` | anything a human should look at: unread rasters, rotations, empty boxes, unverified direction |

**On `lines[]`.** PowerPoint uses `<a:br/>` soft breaks inside a paragraph, and
reading paragraph text joins them into one string. On the V017 deck, this:

```
lock = false;
do {
    while tns(&lock);
```

is **one paragraph**. Three visual lines, one entry. Layer 8 reveals visual
lines, so a merged line means three reveals collapse into one — and the failure
would look like a sequencing bug two layers downstream, not an extraction bug.
The extractor emits `lines[]` alongside `paragraphs[]` and flags the mismatch.

**On connector direction.** This is the most error-prone field in the layer, and
the reason extraction is a script rather than a prompt. `direction_verified` is
set **only** when the XML declares both connection sites *and* an arrowhead;
otherwise it is false with a flag and a stated reason. Nothing is guessed.

---

## Units

`deck extract` keeps native **EMU** and never converts to pixels. Conversion is
lossy, and Layer 5 re-lays-out every slide onto the style contract's grid — so
source pixel values do not survive into the output anyway. What must survive
exactly is text, topology and structure.

Review pages scale positions to a 1920-wide canvas for readability, and say so
in their footer. The manifest holds the authoritative values.
