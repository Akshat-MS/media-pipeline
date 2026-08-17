# Lecture Alive AI — Strategy 2 Playbook
### Version 1 · Prompt Engineering + Layer Output Formats

One document. For each layer: **what it does → the prompt to run → the
artifact it must emit.**

**Version history**
- **v1** — layer structure agreed: global theme separated from entity
  vocabulary; content extraction restored as its own layer (L2A ∥ L2B);
  per-slide semantic resolution split from per-topic visual vocabulary;
  audio moved to a parallel branch.

---

## Project Context (prepend to every session)

> You are a senior professor with recorded lectures — time-based transcript
> plus the original slides. Convert the slides into **guided animation** so
> the session becomes interactive and the visuals stay in sync with the
> narration.

**Four hidden requirements**, none automatic:

| # | Requirement | What it actually means | Solved in |
|---|---|---|---|
| 1 | **Guided** animation | Something directs the eye — the viewer is *led*, not left to scan a static frame | Layer 6 (camera) |
| 2 | **More interactive** | Paced to the learner — momentum, no dead air, visible cause-and-effect | Layer 6 |
| 3 | **Better voice quality** | Same words, cleaner audio | Layer 5 |
| 4 | **Better slide visualisation** | Theme + real diagram vocabulary — not the flat source deck | Layers 1 & 4 |

**Hard constraint:** narration *content* is fixed. Voice quality may improve;
the script and its timing must not change.

**Deliverable set:** 5 videos, each with its own PPTX.

| Video | Duration |
|---|---|
| V017 — OS · Bounded Buffer Problem | 8 min |
| V018 — OS · Reader Writer Problem | 17 min |
| V028 — OS · Banker's Algorithm Overview | 4 min |
| V029 — OS · Banker's Algorithm Data Structures | 8 min |
| V030 — OS · Safety Algorithm | 12 min |

Suggested pilot: **V028** — shortest, and its topic feeds V029/V030.

---

## Layer map

| Layer | What it decides | Scope | Depends on |
|---|---|---|---|
| **0** | Target spec — what the output must be | Project | — |
| **1** | **Global theme** — background, palette (roles unassigned), typography, animation defaults, canvas/encode | Once, all 5 videos | 0 |
| **L2A** | **Asset deconstruction** — what is on each slide | Per slide | — |
| **L2B** | **Timestamp-based transcript** — what is said, when | Per video | — |
| **3** | **Per-slide representation** — resolve semantic identity; layout | Per slide | 1, L2A, L2B |
| **4** | **Visual vocabulary** — icon/shape/line per semantic type | Per topic *(Track 2)* / shared library *(Track 1)* | 1, 3 |
| **5** | **Audio mastering** | Per video, **parallel branch** | 0 |
| **6** | **Sequence / beats** | Per slide | 3, 4, L2B |
| **7** | **Defects & automation boundary** | Project | all |

**Two independent branches.** L2A ∥ L2B run concurrently (mirrors the Phase 1
architecture fork). Layer 5 is a parallel branch that rejoins only at final
mux — it gates nothing upstream.

### The organising principle

- **Layer 1** — decisions made *before* seeing content
- **Layer 2** — facts, no decisions
- **Layer 3** — decisions made *because of* the facts
- **Layer 4** — how those decisions look

---

## Format follows consumer

| Layer | Emits | Architectural role | Track 1 consumer | Scope |
|---|---|---|---|---|
| 0 | requirements register | Acceptance criteria | Humans; cited by all | Project |
| 1 | `global_style_contract.json` | **Presentation (global)** | Config Mgmt | Global |
| L2A | `manifest.json` | **Content** | `asset_deconstructor` | Per slide |
| L2B | `transcript.json` | **Content** | Transcript Alignment | Per video |
| 3 | `slide_representation.json` | **Semantic + layout** | Sequence Mapping | Per slide |
| 4 | `visual_vocabulary.json` | **Presentation (topic)** | Resource Library | Per topic |
| 5 | `audio_profile.json` + master | Audio config | Audio stage | Per video |
| 6 | `sequence.json` | **Sequence/timing** | Renderer | Per slide |
| 7 | `automation_boundary` | Build decisions | Roadmap | Project |

Layers 0 and 7 are human decision records → tables with a thin JSON slice.
Layers 1–6 are machine inputs → strict JSON.

**Versioning.** Phase 1's `SchemaEnvelope` (`models/envelope.py`) + migration
chain are these artifacts' first real customers. Every JSON artifact is wrapped:

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "<name>",
  "generated_at": "2026-08-15T00:00:00Z",
  "source": "layer_N_manual",
  "payload": { }
}
```

Iterating a layer = bump version + register a migration. Not overwrite-and-hope.

---

## How Layer 0 feeds every later layer

**Rule: attach the registers in full; scope attention with IDs in the prompt.**

The Layer 0 registers are three files, split by what they hold:

| File | Holds |
|---|---|
| `shared/requirements/delivery-targets.md` | TGT-001…011 — numeric, post-render |
| `shared/requirements/visual-grammar.md` | VGR-01…07 — behavioural, generation-time |
| `shared/requirements/findings-and-decisions.md` | RC / DEC / PROP |
| `shared/requirements/competitive-analysis.md` | evidence only, rarely needed |

Do not paste subsets — a pasted subset is a second copy, and copies drift. But
an unscoped attachment is also wrong: a model handed the whole register will
try to satisfy audio bitrate targets while being asked about typography.

Every layer prompt opens with:

> **Inputs:** the Layer 0 registers.
> Use only: [ID list]. Ignore all other entries.
> If a requirement outside that list appears relevant, name it and stop —
> do not act on it.

| Layer | Use only |
|---|---|
| 1 | VGR-02, VGR-03, TGT-001…004 |
| L2A | VGR-01 |
| L2B | VGR-05, DEC-001 |
| 3 | VGR-01, VGR-07 |
| 4 | VGR-02, VGR-04 |
| 5 | TGT-005…010, RC-003 |
| 6 | VGR-03, VGR-05, VGR-07, TGT-011, RC-002 |
| 7 | whichever IDs the defect touches |

The "name it and stop" clause surfaces mis-routed requirements instead of
letting the model quietly act outside its scope.

---

# LAYER 0 — Target Spec ✅ COMPLETE

### What it does
Establishes what the final output must be. The three-way comparison
(original / ours / competitor) is *evidence*, not the artifact.

### Output
the Layer 0 registers:

| Register | Species | Enforced by |
|---|---|---|
| **TGT-0xx** | Numeric delivery targets | Post-render validation gates |
| **VGR-0x** | Behavioural rules | Module logic *(owned by `visual_grammar_requirements.md`)* |
| **RC-00x** | Root-cause findings | Change *how* something is built |
| **DEC / PROP** | Open decisions | — |

### Governance
IDs immutable and append-only; retire by `status`, never by deletion;
Register B descriptions edited only in `visual_grammar_requirements.md`.

---

# LAYER 1 — Global Style Contract

### What it does
Selects the **theme** for the series: background, palette, typography,
animation defaults, canvas/encode. One-time activity, shared by all 5 videos.

**Layer 1 contains no entity grammar.** No shapes, no icons, no
entity→colour assignments. Process/resource/edge vocabulary is
Deadlock-specific; producer/consumer/buffer is Bounded-Buffer-specific.
Those belong to Layer 4.

**Palette roles are named but unassigned.** A colour is defined as meaning
*blocked/waiting*; which entity claims that role is decided per topic. This
keeps colour *meaning* consistent across all five videos while letting the
vocabulary differ.

**The theme is a fresh design choice for engagement** — not derived from the
customer's decks. Those are content, not a style reference.

### Runs in two steps — do not collapse them

JSON records a decision; it does not make one. And **a theme cannot be judged
from a written description** — step 1 must render real visual samples.

## Layer 1 · Step 1 — propose and render theme directions

> **Inputs:** the Layer 0 registers.
> Use only: VGR-02, VGR-03, TGT-001…004. Ignore all other entries.
> If a requirement outside that list appears relevant, name it and stop.
>
> Propose **3–4 theme directions** for an educational animation series
> (5 OS-topic videos sharing one visual identity). Themes are chosen for
> **student engagement and legibility** — not derived from the customer's
> existing decks, which are content only.
> Cover a genuine range (e.g. dark, light, and one alternative direction).
>
> **Render each as a visual sample**, 16:9, sized to represent 1920×1080
> output. Each sample shows: a title, 3–4 bullet lines at realistic body
> size, and a placeholder diagram area using **neutral unlabeled geometry**
> (plain nodes and connectors).
> Placeholder geometry is deliberate — entity vocabulary is Layer 4. Judge
> these on background, palette contrast, typography legibility and tone only.
>
> For each theme also state: rationale (2–3 sentences); the palette **with a
> semantic role named per colour** (e.g. "this colour always means
> blocked/waiting") but **not assigned to any entity**; typography pairing
> with a legibility rationale at 1080p; and trade-offs.
>
> Do not assign colours to diagram entities. Do not define shapes or icons.
> Do not produce JSON.

**Review at true scale before committing.** A sample viewed small in a chat
window reads as legible even when the body size would fail on a projector.
TGT-001 (1080p) implies real pixel sizes that only matter when seen full-screen.

### Step 1 output — theme decision record (table, not JSON)

| Field | Value | Rationale |
|---|---|---|
| Theme name | | |
| Background treatment | | |
| Palette + semantic roles (unassigned) | | |
| Typography pairing | | legibility at 1080p |
| Rejected alternatives | | why |

**Must-measure list**

| Value | Source | Status |
|---|---|---|
| body/title pixel sizes verified full-screen | rendered sample | pending |

## Layer 1 · Step 2 — serialize

> Here is the approved theme decision. Serialize it as the global style
> contract JSON: canvas and output encode; background; palette with semantic
> roles (unassigned); typography; animation dimension defaults and usage
> rules (reveal, state motion, camera).
> Each entry carries a `satisfies` field (VGR-xx / TGT-xxx) or a one-line
> rationale. Values that must be measured stay `null`.
> **Do not include entity grammar** — no shapes, icons, or per-entity colour
> assignments. If something appears to require one, list it as an open
> question for Layer 4 instead.

### Step 2 output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "global_style_contract",
  "payload": {
    "version": "v1",
    "canvas": {
      "width": 1920, "height": 1080, "fps": 30,
      "safe_margin_px": null,
      "satisfies": ["TGT-001", "TGT-002"]
    },
    "background": { "treatment": null, "base_color": null },
    "palette": {
      "roles": [
        {"role": "blocked_waiting", "color": null, "rationale": null},
        {"role": "granted_active", "color": null, "rationale": null},
        {"role": "neutral_structure", "color": null, "rationale": null},
        {"role": "focus_attention", "color": null, "rationale": null}
      ],
      "note": "roles are NOT assigned to entities here — Layer 4 assigns them"
    },
    "typography": {
      "title": {"family": null, "size_px": null},
      "body": {"family": null, "size_px": null},
      "label": {"family": null, "size_px": null},
      "legibility_verified_fullscreen": false
    },
    "animation_defaults": {
      "reveal": {"default_duration_s": 0.3, "variants": ["fade_in", "draw_on"]},
      "state_motion": {"usage_rule": "teach a mechanic only — never decorative", "satisfies": ["VGR-04"]},
      "camera": {
        "variants": ["zoom_to_focus", "pan_between_regions", "pull_back_summary"],
        "rules": [
          "camera follows the narration subject",
          "never move camera and reveal a new element simultaneously"
        ],
        "satisfies": ["VGR-03"]
      },
      "layering": {"rule": "dimensions compose on one element, not either/or", "satisfies": ["VGR-02"]}
    },
    "output_encode": {
      "video_codec": "h264_high", "video_bitrate_mbps": [8, 12],
      "audio": "aac 48000 stereo",
      "satisfies": ["TGT-003", "TGT-004"]
    }
  }
}
```

---

# LAYER 2 — Content Extraction

**Facts only, no decisions.** L2A and L2B run in parallel.

> **Note:** in Strategy 2 this layer is **hand-produced** — manually doing
> what `asset_deconstructor` and Transcript Alignment will later do in code.
> That is the point: it stress-tests the schemas before the modules exist.
> It is not a creative prompt-engineering step.

## LAYER 2A — Asset Deconstruction (per slide)

### What it does
Extracts what is on the slide as structured data. No styling, no
interpretation.

### Prompt

> **Inputs:** the Layer 0 registers. Use only: VGR-01.
>
> Extract this slide's content as JSON: `slide_id`; `metadata`
> (extraction_path, canvas_dimensions, has_diagram, diagram_implied);
> `assets[]` with element_id, type, shape_kind, tag (STATIC/DYNAMIC),
> semantic_type, bounding_box, endpoints (start/end anchor_element_id),
> properties (text, instance_count, indent_level, parent_id).
>
> Rules: set `semantic_type` **only** where geometry or typography alone
> determines it. If identity depends on narration context (e.g. whether an
> arrow is a request or an assignment edge), leave it `null` and record the
> visual signal under `semantic_type_prior`.
> Per VGR-01, capture formal notation **verbatim** — never simplify or drop
> it. Do not infer anything not visually present.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "slide_manifest",
  "payload": {
    "slide_id": "v028_slide_03",
    "metadata": {
      "extraction_path": "manual_l2a",
      "canvas_dimensions": {"width": 1920, "height": 1080},
      "has_diagram": true,
      "diagram_implied": false
    },
    "assets": [
      {
        "element_id": "n1",
        "type": "shape", "shape_kind": "ellipse", "tag": "DYNAMIC",
        "semantic_type": null,
        "bounding_box": {"x": 230, "y": 340, "w": 76, "h": 44},
        "endpoints": null,
        "properties": {"text": "P1", "instance_count": null, "parent_id": null}
      },
      {
        "element_id": "e_n1_n2",
        "type": "connector", "shape_kind": "arrow", "tag": "DYNAMIC",
        "semantic_type": null,
        "semantic_type_prior": {"value": null, "basis": "color:red", "confidence": null},
        "bounding_box": {"x": 250, "y": 210, "w": 90, "h": 140},
        "endpoints": {"start": {"anchor_element_id": "n1"}, "end": {"anchor_element_id": "n2"}},
        "properties": {}
      }
    ]
  }
}
```

## LAYER 2B — Timestamp-Based Transcript (per video)

### What it does
Produces what was said and when. **Two granularities — they gate different
layers:**

| Granularity | Gates | Notes |
|---|---|---|
| Transcript + **segment-level** timing | Layer 3 | enough to know which segment discusses which element |
| **Word/phrase-level** timestamps | Layer 6 only | DEC-001 — needed to time sub-clause motion |

DEC-001 therefore remains deferrable until Layer 6. Under the current audio
default (clean the original human recording), word-level timestamps require
**forced alignment** (e.g. WhisperX); TTS would supply them natively but is
rejected on voice-identity grounds.

**Source audio:** extract from the original lecture recording, never from a
previous output and never the ASR-downsampled copy (RC-003).

```
ffmpeg -i V028.mp4 -vn -c:a copy audio.m4a
```

### Prompt

> **Inputs:** the Layer 0 registers. Use only: VGR-05, DEC-001.
>
> Produce the transcript with timing. Emit segment-level start/end for every
> segment. Where word/phrase-level timestamps are available, include them —
> flag clearly if they are not, since Layer 6 depends on them.
> Transcribe verbatim: do not clean up, summarise, or reorder speech.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "transcript",
  "payload": {
    "video_id": "V028",
    "granularity": "segment",
    "word_level_available": false,
    "segments": [
      {
        "segment_id": "t_045",
        "start_s": 12.40, "end_s": 14.90,
        "text": "consider process P1 which requests resource R1",
        "words": null
      }
    ]
  }
}
```

---

# LAYER 3 — Per-Slide Representation

### What it does
The first layer that makes decisions **because of** the content. Two jobs:

1. **Resolve semantic identity** — fill the `null` `semantic_type`s from L2A
   using the transcript from L2B. This is where "is this red arrow a request
   or an assignment edge" is decided.
2. **Choose layout** — per slide. Split-panel, vertical split, diagram-only,
   full-bleed text. Not a global convention; some slides want a horizontal
   split.

**Depends on both L2A and L2B.** Scope is **per slide**.

### Prompt

> **Inputs:** the slide manifest (L2A), the transcript (L2B),
> the Layer 0 registers. Use only: VGR-01, VGR-07.
>
> For each asset with `semantic_type: null`, resolve it using the narration
> that discusses this slide. State the evidence for each resolution — quote
> the transcript segment id. Where the narration does not disambiguate, leave
> it null and flag it rather than guessing.
> Treat `semantic_type_prior` (e.g. colour) as a hint, not proof — if the
> narration contradicts the prior, the narration wins; note the conflict.
>
> Then choose this slide's layout from the content: which regions exist,
> what each holds, and why that split suits this slide's material.
>
> Per VGR-07, confirm every narrated point on this slide has a corresponding
> element; list anything narrated with no visual.
> Do not assign shapes, icons, or colours — that is Layer 4.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "slide_representation",
  "payload": {
    "slide_id": "v028_slide_03",
    "manifest_ref": "v028_slide_03.manifest.json",
    "transcript_ref": "V028.transcript.json",
    "resolved_semantics": [
      {
        "element_id": "e_n1_n2",
        "semantic_type": "request_edge",
        "evidence": {"segment_id": "t_045", "basis": "narration states P1 requests R1"},
        "prior_agreed": true,
        "confidence": null
      }
    ],
    "unresolved": [
      {"element_id": "e_n4_n5", "reason": "narration does not distinguish direction"}
    ],
    "layout": {
      "type": "split_vertical",
      "regions": [
        {"id": "left", "holds": "bullet_text"},
        {"id": "right", "holds": "diagram"}
      ],
      "rationale": null
    },
    "coverage_check": {
      "narrated_points_without_visual": [],
      "satisfies": ["VGR-07"]
    }
  }
}
```

---

# LAYER 4 — Visual Vocabulary

### What it does
Decides **what each semantic type looks like** — icon, shape, line treatment,
and which Layer 1 palette role it claims.

**Dual scope by track:**

| Track | Scope | Behaviour |
|---|---|---|
| **Track 1** (code/design) | Shared **Resource Library** across all 5 videos | Look up the semantic type; add it if absent. Accumulates. |
| **Track 2** (prompt method) | Per video | Each video's vocabulary defined in its own pass |

The per-video passes are how the shared library gets populated over time.

### Prompt

> **Inputs:** the global style contract (Layer 1), the resolved semantic
> types for this video (Layer 3), the Layer 0 registers.
> Use only: VGR-02, VGR-04.
>
> For each semantic type in this video, decide: shape, icon treatment, line
> style (for connectors), and **which Layer 1 palette role it claims**.
> Do not introduce colours outside the global palette — claim a role from it.
> Justify each by a VGR-xx requirement or a one-line pedagogical reason.
> Where two semantic types could be confused visually, state how the design
> disambiguates them.
> Per VGR-04, state the dynamic-state motion treatment for every stateful
> type — not just a special-cased few.
> Flag any type that needs a component the Resource Library does not have.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "visual_vocabulary",
  "payload": {
    "topic": "bankers_algorithm",
    "applies_to": ["V028", "V029", "V030"],
    "global_contract_version": "v1",
    "entities": [
      {
        "semantic_type": "process",
        "shape": null, "icon_ref": null,
        "palette_role": null,
        "label_position": null,
        "state_motion": null,
        "justification": null
      },
      {
        "semantic_type": "request_edge",
        "shape": "connector", "line_style": null,
        "palette_role": "blocked_waiting",
        "arrowhead_at": null,
        "state_motion": null,
        "justification": null,
        "disambiguated_from": "assignment_edge"
      }
    ],
    "resource_library_gaps": []
  }
}
```

---

# LAYER 5 — Audio Mastering (parallel branch)

### What it does
Improves delivered sound quality. **Gates nothing upstream** — rejoins only at
final mux.

Mastering makes audio *sound* better; it contributes nothing to knowing *what
was said when*. Transcription and alignment read the raw audio independently.

**Constraint:** narration content fixed, professor's own voice retained.
Quality may improve; the voice may not be replaced.

- Master each video's **full duration continuously** — never chunk.
  Loudness normalization is integrated across the program; chunking then
  concatenating produces audible level jumps.
- All five videos normalize to the **same** TGT-009 target, which gives
  cross-video consistency by construction.
- **Music bed:** deferred. Review video 1 without one so dead air is audible
  and gets fixed at the visual layer. Never used as a pacing fix.

### Prompt

> **Inputs:** original lecture audio, the Layer 0 registers.
> Use only: TGT-005…010, RC-003.
>
> Analyse the source narration: sample rate, channels, bitrate, mean and peak
> loudness, noise characteristics.
> Recommend a processing chain to improve perceived quality **without
> altering timing or content**, and state the realistic ceiling given the
> source fidelity.
> Output both the JSON profile and a runnable ffmpeg command.

**Execution is a script, not a prompt.** Denoise → normalize → EQ → encode is
deterministic. The prompt produces the *specification*; ffmpeg does the work.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "audio_profile",
  "payload": {
    "path": "clean_original",
    "narration_content": "immutable",
    "voice": "professor_original_retained",
    "processing_chain": ["denoise", "loudness_normalize", "eq"],
    "output": {"sample_rate": 48000, "channels": 2, "codec": "aac", "bitrate_kbps": null},
    "target_loudness_lufs": -16,
    "peak_ceiling_db": -1.0,
    "measured_source": {"mean_db": null, "peak_db": null, "noise_floor_db": null},
    "realistic_ceiling_note": null,
    "satisfies": ["TGT-005", "TGT-006", "TGT-007", "TGT-008", "TGT-009", "TGT-010", "RC-003"]
  }
}
```

---

# LAYER 6 — Sequence / Beats

### What it does
Turns representation + vocabulary + narration timing into timed beats. This is
where the sync and pacing defects are fixed.

**Two mandatory fields per beat — `dimension` and `narration_ref` —
structurally prevent both known defects:** you cannot emit a flat all-reveals
sequence (dimension is explicit), and you cannot emit a fixed pause (there is
nowhere to put one).

**This is where word/phrase-level timestamps become necessary** (DEC-001).

### Prompt

> **Inputs:** slide representation (Layer 3), visual vocabulary (Layer 4),
> transcript (L2B), the Layer 0 registers.
> Use only: VGR-03, VGR-05, VGR-07, TGT-011, RC-002.
>
> Build the animated sequence as JSON. For each beat give: `beat_id`,
> `t_start_s`, `narration_ref` (segment id + word offset where available),
> `dimension` (reveal | state_motion | camera), `action`, `targets`
> (element_ids), `duration_s`.
>
> Rules: every beat binds to narration timing — no fixed sleeps (RC-002).
> Every beat names its dimension. Do not move the camera and reveal a new
> element in the same beat (VGR-03). Dimensions may layer on one element
> (VGR-02). Flag any gap beyond the dead-air threshold.
> Per TGT-011 the sequence must span the full narration — no silent trimming.

### Output

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "slide_sequence",
  "payload": {
    "slide_id": "v028_slide_03",
    "representation_ref": "v028_slide_03.representation.json",
    "vocabulary_ref": "bankers_algorithm.vocabulary.json",
    "global_contract_version": "v1",
    "beats": [
      {
        "beat_id": "b01",
        "t_start_s": 12.40,
        "narration_ref": {"segment_id": "t_045", "word_offset": null, "text_hint": "consider process P1"},
        "dimension": "camera",
        "action": "zoom_to_focus",
        "targets": ["n1"],
        "duration_s": 0.8
      },
      {
        "beat_id": "b02",
        "t_start_s": 13.20,
        "narration_ref": {"segment_id": "t_046", "word_offset": null, "text_hint": "requests resource R1"},
        "dimension": "state_motion",
        "action": "token_travel",
        "targets": ["e_n1_n2"],
        "duration_s": 1.1
      }
    ],
    "validation": {
      "max_dead_air_s": null,
      "all_beats_narration_bound": true,
      "covers_full_narration": null
    }
  }
}
```

---

# LAYER 7 — Defects & Automation Boundary

### What it does
Logs each defect and how hard it was to fix. **The `rounds` column is the real
payload** — it is the evidence for which Track 1 modules are worth automating.

### Prompt (per defect — one at a time)

> This specific defect: [describe]. Fix only this, referencing the existing
> contracts and beat sheet. Do not restate or regenerate the whole scene.

### Output — table

| ID | Slide | Defect | Category | Fix prompt (short) | Rounds | Verdict |
|---|---|---|---|---|---|---|
| DEF-001 | s03 | token fired before narration | sync | "bind b02 to t_046" | 1 | automate |
| DEF-002 | s03 | camera move felt arbitrary | camera | (several vague attempts) | 4 | human/taste |

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "automation_boundary",
  "payload": {
    "rule": "1-2 rounds => good automation candidate; 3+ vague rounds => leave to human",
    "verdicts": [
      {"module": "sequence_timing", "verdict": "automate", "evidence": ["DEF-001"]},
      {"module": "camera_direction", "verdict": "human_owns_taste", "evidence": ["DEF-002"]}
    ]
  }
}
```

The 1–2 vs 3+ rule is a **starting heuristic, not settled** — some defects take
many rounds because the first prompt was badly framed. Revisit after ~10 entries.

---

# Per-Slide Capture Log

Copy per slide.

### Slide: [id]

- **Global contract version:** v___
- **L2A manifest:** `[ref]`
- **L2B transcript ref + granularity:** `[ref]`
- **Layer 3 resolutions** (element → semantic_type → evidence segment):
- **Unresolved / flagged:**
- **Layout chosen + why:**
- **Layer 4 vocabulary entries used / added:**
- **Beat sheet:**

| t (s) | dimension | action | target(s) | duration |
|---|---|---|---|---|
| | | | | |

- **Defects → Layer 7:**
- **Rounds to resolve each:**
- **Final approved output:**
- **Notes for Track 1:** *(schema gaps, timing patterns worth encoding,
  anything the manifests couldn't represent)*
- **New Layer 0 rows discovered:**

---

# Handoff — what Track 1 receives

1. `global_style_contract.json` → Config Mgmt presentation config
2. `visual_vocabulary.json` per topic → seeds the shared **Resource Library**
3. N × `manifest.json` → test fixtures + schema validation for `asset_deconstructor`
4. N × `slide_representation.json` → target output for semantic resolution
5. N × `sequence.json` → target output for Sequence Mapping; input for Renderer
6. `audio_profile.json` + ffmpeg chain → audio stage implementation
7. `automation_boundary.json` → which modules to build vs. leave manual
8. The three Layer 0 registers → acceptance criteria

Items 1, 2 and 7 are highest-value: two are config you would otherwise design
blind, the third prevents building automation nobody needs.

---

# Working order

1. **Layer 0** — done
2. **Layer 1** — theme, once, for all five videos *(step 1 renders samples;
   review full-screen before approving step 2)*
3. **L2A ∥ L2B** on the pilot video (V028) — run in parallel
4. **Layer 3** — one slide
5. **Layer 4** — vocabulary for that topic
6. **Layer 6** — beats for that one slide
7. **Layer 7** — log defects
8. Revise Layers 1/4 from what slide 1 taught you — expect this
9. Then the rest of V028, then the remaining videos

**Layer 5** runs any time before final mux — it is a parallel branch.

Doing one slide end-to-end first means eating the contract revision once
instead of propagating a wrong decision across five videos.
