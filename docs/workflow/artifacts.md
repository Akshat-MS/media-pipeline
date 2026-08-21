# Artifacts

**What exists, who produced it, who reads it.** Append a row whenever a layer
produces something another prompt or module consumes.

**The rule.** A prompt's Inputs section **cites path + version. It never pastes
the content.** A pasted copy is a second owner of the same fact, and copies
drift.

**How to use the Scope column.** It tells you what to attach:

| Scope | Attach to |
|---|---|
| `project` | most prompts — but always scoped by ID inside the prompt |
| `global` | any layer that needs the visual system |
| `per topic` | layers working on that topic's videos |
| `per video` | layers working on that video |
| `per slide` | the next layer for that slide only |

---

## 1 · Source inputs

Not produced by any layer. The raw material.

| Input | What it is | Used by |
|---|---|---|
| 5 source lecture recordings | V017, V018, V028, V029, V030 | Layer 4 (transcript), Layer 7 (audio) |
| 5 source PPTX decks | one per video | Layer 3 (asset deconstruction) |
| V017 missing slide | reconstructed from a video frame; normalised and merged at position 2 | Layer 3 |
| Previous output video | our earlier attempt | Layer 1 (evidence) |
| Competitor output video | the comparison bar | Layer 1 (evidence) |
| Client feedback | quoted verbatim | Layer 1 (evidence) |

**Note:** source video and audio are **never attached to a prompt** — they are
processed locally by ffmpeg / ffprobe and only the *derived text or numbers* are
attached. See `README.md` §7.

---

## 2 · Produced artifacts

| Artifact | Path | Form | Produced by | Consumed by | Scope | Version | Status |
|---|---|---|---|---|---|---|---|
| Delivery targets | `docs/shared/requirements/delivery-targets.md` | md + JSON slice | 1 | 2, 7, 9; validation gates | project | v1 | current |
| Visual grammar | `docs/shared/requirements/visual-grammar.md` | md + JSON slice | 1 | 2, 3, 5, 6, 8 | project | v1 | current |
| Findings & decisions | `docs/shared/requirements/findings-and-decisions.md` | md + JSON slice | 1 | 4, 7, 8, 9 | project | v1 | current |
| Competitive analysis | `docs/shared/requirements/competitive-analysis.md` | md | 1 | provenance only | project | v1 | current |
| Style contract (document) | `docs/shared/specs/style-contract.md` | md | 2 | 5, 6, 8 | global | **v3** | current |
| Style contract (runtime) | `res/config/style/global_style_contract.json` | JSON | 2 | 6, 8; renderer | global | **v1** | ⚠ see OBS-006 |
| Theme specimens | `docs/shared/specimen/specimen-{navy,blue,green}.html` | HTML | 2 | human review; renderer reference | global | v3 | current |
| Specimen fonts | `docs/shared/specimen/fonts/*.ttf` | TTF | 2 | render host | global | — | current |
| Design decisions workbook | `docs/shared/workbooks/design-decisions.xlsx` | xlsx | 1 | provenance only | project | — | current |
| V017 deck, 5 slides | `res/inputs/V017-bounded-buffer.pptx` | pptx | source + `mpk deck merge` | 3 | per video | v2 | **not tracked** |
| V017 raw shape tree | `res/workdir/v017.raw.json` | JSON | `mpk deck extract` | 3 | per video | v1 | **not tracked** |
| V017 raw ASR | `res/workdir/v017.asr.json` | JSON | `mpk transcript build` | 4 | per video | v1 | **not tracked** |
| V017 step-3 proposals | `res/workdir/v017.verified.json` | JSON | Layer 4 prompt | 4 step 5 | per video | v1 | **not tracked** |
| V017 human review | `res/workdir/v017.review.txt` | text | **a human, listening** | `mpk transcript apply` | per video | v1 | **not tracked** |
| **V017 narration timeline** | `res/workdir/v017.transcript.json` | JSON | `mpk transcript apply` | **5, 8** | per video | v1 | **not tracked** |
| V017 transcript review page | `res/workdir/v017.transcript.html` | HTML | `mpk transcript export` | human review | per video | v1 | **not tracked** |
| **V017 windows + slide identity** | `res/workdir/v017.changes.json` | JSON | `mpk video slidechanges --deck` | **5, 8** | per video | v2 | **not tracked** |
| V017 window review page | `res/workdir/v017.changes.html` | HTML | same command, `--html` | human review | per video | v2 | **not tracked** |
| ekLakshya brand assets | `res/library/icons/` | png + jpeg | supplied + derived | 2 (contract v6) | project | v1 | **tracked** |
| Footer specimen | `docs/shared/specimen/footer-themes.html` | HTML | Layer 2 | human review | global | v2 | current |
| Audio master, 48 kHz stereo | `res/workdir/<v>-master.wav` | wav | `mpk audio extract` | 7, final mux | per video | — | **not tracked** |
| Audio ASR copy, 16 kHz mono | `res/workdir/<v>-asr.wav` | wav | `mpk audio asr` | 4 | per video | — | **not tracked** |
| Raw ASR output | `res/workdir/<v>.asr.json` | JSON | `mpk transcript build` | 4 (verify) | per video | — | **not tracked** |
| Narration timeline | `res/workdir/<v>.transcript.json` | JSON | 4 | 5, 8 | per video | — | **not tracked** |

**`res/` is gitignored per-job data** (`res/inputs/*`, `res/workdir/*`,
`res/outputs/*` — folders kept via `.gitkeep`). Decks, extractions, renders and
outputs live there and are **not committed**. This register records where they
belong, not that git holds them. Anything that must survive a fresh clone goes
under `docs/` or `tools/`.

⚠ **The two style-contract rows disagree on version.** The document says v3, the
runtime JSON says v1. Tracked as OBS-006. Until it is resolved, cite the
*document* as authoritative and treat the JSON as not yet regenerated.

---

## 3 · Pre-existing engineering artifacts

Built in Phase 1, before this playbook. Layers cite them; layers do not produce
them.

| Artifact | Path | Relevance |
|---|---|---|
| Quality thresholds | `docs/shared/requirements/quality-thresholds.md` | Numeric gates. Overlaps TGT-003…008 — **TGT owns the value** where they disagree |
| Threshold code | `src/pipeline/validation/thresholds.py` | The gates as implemented |
| Validators | `src/pipeline/validation/validators.py` | One function per check |
| Schema envelope | `src/pipeline/models/envelope.py` | The wrapper every artifact is supposed to conform to — **it does not currently match any artifact**, see OBS-013 |
| Migration chain | `src/pipeline/models/migrations.py` | Registered migrations — **currently empty**, see OBS-014 |
| Asset deconstructor schema | `docs/shared/specs/asset-deconstructor-schema.md` | Target shape for Layer 3 output |
| Architecture decision records | `docs/adr/ADR-001…006` | Phase 1 decisions: language, state store, module boundaries, resumability, schema versioning, testing |
| ADR-007 · Config Mgmt | `docs/adr/ADR-007-config-mgmt.md` | Eight decisions covering how the style contract is loaded, validated, versioned and theme-resolved |
| Style contract loader | `src/pipeline/services/config/loader.py` | **The contract's runtime consumer.** Reads, migrates if needed, validates via `StyleContract` |
| Theme resolver | `src/pipeline/services/config/resolver.py` | Flattens the selected theme into one token set; default `navy` |
| Encode drift test | `tests/unit/test_config_delivery_targets_sync.py` | Asserts the contract's `output_encode` matches TGT-003…008 as owned by `delivery-targets.md` |

### Tooling

| Artifact | Path | Purpose |
|---|---|---|
| **mpk** — Media Pipeline Kit | `tools/mpk.py` | Deterministic CLI: deck extract/normalize/merge/render, review build, audio and video probes, manifest check |
| Review templates | `tools/templates/` | One page per review kind. `mpk review templates` lists them; `mpk review build -t <name>` picks one |
| ↳ Slide review | `tools/templates/slide-review.html` | Layer 3's review page — its embedded JS renders the manifest. `mpk review build` only injects data |
| ↳ Transcript review | `tools/templates/transcript-review.html` | Layer 4's page — two-column time \| text, audio embedded, click a word to play just that word |

**Planned templates**, as their layers are written: `vocabulary-review`
(Layer 6), `sequence-player` (Layer 8 — the beat sheet with transport, caption
bar and speed control, per the dry run). Each is a template filled with data,
never a second renderer.
| Gap specimens | `docs/shared/specimen/issues-specimen/` | Rendered evidence for each Layer 2 defect found (background, grid, legibility, math, notation, palette) |

### Superseded by this playbook

| Old artifact | Superseded by | Note |
|---|---|---|
| `docs/workflow/playbook.md` | `docs/workflow/README.md` + per-layer files | Old layer numbering (0-based; theme was Layer 1) |
| `docs/workflow/layer-captures/layer1-token-schema-and-prompt.md` | `2-global-theme.md` | Its token-schema technique, chrome/type-style split and round-trip verification are merged in. **Retain as provenance** — it is the record of the first prompt repair (see `prompt-changelog.md` PC-000) |

---

## 4 · Inputs for the next prompt — Layer 2, Global Theme

Layer 2's work is already complete; this records what its prompt consumes, so the
layer file can be written against reality.

### Attach

| Input | Path | Why |
|---|---|---|
| Delivery targets | `docs/shared/requirements/delivery-targets.md` | scoped to **TGT-001…004** |
| Visual grammar | `docs/shared/requirements/visual-grammar.md` | scoped to **VGR-02, VGR-03** |

Attach both **in full** and scope attention inside the prompt:

> Use only: VGR-02, VGR-03, TGT-001…004. Ignore all other entries. If a
> requirement outside that list appears relevant, name it and stop.

A pasted subset would be a second copy; an unscoped attachment makes the model
try to satisfy audio bitrate targets while being asked about typography.

### Explicitly NOT an input

| Not an input | Why |
|---|---|
| The customer's source decks | The theme is a **fresh design choice for engagement**. The decks are content, not a style reference. Deriving the theme from them reproduces the flat original |
| `findings-and-decisions.md` | No RC or DEC bears on theme selection |
| `competitive-analysis.md` | Evidence only; the requirements already carry what matters |

### Non-file inputs the prompt depends on

These are easy to forget because they are not attachments.

| Requirement | Why it matters |
|---|---|
| **Ability to render real visual samples** (HTML at 16:9, 1920×1080) | A theme cannot be judged from a written description. Step 1 must produce something you can look at |
| **The four fonts installed or linked** — Space Grotesk, Inter, Space Mono, Source Serif 4 | A specimen rendered in fallback fonts tests the wrong thing |
| **A real 1080p display** | Reviewing a sample small in a chat window makes 20px body text look fine when it would fail on a projector. Full-screen review is a required step, not a nicety |
| **A contrast checker** | The contrast and colour-blindness figures in the contract are measured, not estimated — that is why they are trustworthy |

### Layer 2 produces

| Output | Consumed by |
|---|---|
| Style contract document + runtime JSON | Layers 6, 8; renderer |
| Theme specimens (one per variant) | Human review; renderer reference |

---

## Governance

- Append a row when an artifact is produced. Never delete a row — retire by
  `status` (`current` / `superseded by <path>` / `stale`).
- The `Version` column is the artifact's own payload version, not its
  `schema_version`. Where the two disagree, that is an open item.
- If an artifact has no entry in `Consumed by`, ask whether it should exist at
  all — an artifact nobody reads is cost without benefit.

## Changelog

- **v1** — initial register. Records Layer 1 and Layer 2 outputs, source inputs,
  pre-existing Phase 1 artifacts, and the Layer 2 input set.
