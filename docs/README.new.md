# Lecture Alive AI — Documentation

Local-first pipeline that takes a slide deck (PPTX) plus a lecture video (MP4)
and produces an aligned, animated, narration-synced output video.

**Deliverable set:** 5 Operating Systems lectures — V017 (Bounded Buffer, 8m),
V018 (Reader Writer, 17m), V028 (Banker's Overview, 4m), V029 (Banker's Data
Structures, 8m), V030 (Safety Algorithm, 12m). Pilot: **V028**.

---

## Two tracks

| Track | What it is | Folder |
|---|---|---|
| **engine** | The automated pipeline — the tool itself | `docs/engine/` |
| **workflow** | Prompt-driven authoring — produces the client deliverable *and* the ground-truth artifacts the engine consumes | `docs/workflow/` |
| **shared** | Consumed by both | `docs/shared/` |

**Placement rule:** a file lives where it is *consumed*, not where it was
produced. The style contract is authored by the workflow track but consumed by
both — so it sits in `shared/specs/`.

---

## Status

| Item | Status |
|---|---|
| Engine — Phase 1 foundations | ✅ complete (`phase1-complete`) |
| Engine — Config Mgmt | ▶ next build — see `engine/config-mgmt-handoff.md` |
| Engine — `asset_deconstructor` | ◐ design ~60% — 2.2 and 2.4 open |
| Workflow — Layer 0 target spec | ✅ complete |
| Workflow — Layer 1 style contract | ✅ complete, approved |
| Workflow — L2A / L2B extraction | ⛔ blocked — needs the real V028 `.pptx` and audio |

---

## Map

```
docs/
  README.md                       this file
  adr/                            architecture decision records (append-only)
  engine/
    architecture.md               pipeline architecture, containers, Stage contract
    config-mgmt-handoff.md        implementation brief for Config Mgmt
  workflow/
    playbook.md                   layer-by-layer prompt playbook (Layers 0–7)
    layer-captures/               per-layer prompts and captured output
  shared/
    requirements/
      layer0-requirements.md      TGT / VGR / RC / DEC / PROP registers
      visual-grammar.md           VGR rule descriptions (source of truth)
    specs/
      style-contract.md           Layer 1 token table — the design spec
      asset-deconstructor-schema.md
    workbooks/
      design-decisions.xlsx       all finalized tables, read-only overview
    specimen/
      specimen-navy|blue|green.html/.png
      specimen-navy-grid.png      grid overlay
      compare-themes.html/.png    three-way comparison
      fonts/                      4 TTFs required by the contract
      issues-specimen/            the six design-gap demonstrations
res/                              runtime data (already in the repo)
  config/style/global_style_contract.json   artifact Config Mgmt loads
  library/{components,icons,templates}      Resource Library (Layer 4)
  inputs/ outputs/ workdir/                 transient, gitignored
```

---

## Document types and their update rules

Mixing these is what makes documentation rot, so they are kept apart.

| Type | Update rule | Where |
|---|---|---|
| **Decision records** — *why* | append-only, never edited, cited by ID | `adr/` |
| **Registers** — *what we require* | append-only by ID, retire via `status` | `shared/requirements/` |
| **Specifications** — *what is true now* | overwritten in place, internal changelog | `shared/specs/` |
| **Working docs** — *how to continue* | disposable once consumed | `engine/`, `workflow/` |

**Rules**
- One home per fact. Everything else cites it rather than restating it.
- IDs are immutable and append-only — never renumber, never reuse. Retire by
  `status` (`rejected`, `superseded_by: <ID>`), never by deleting a row.
- Version lives *inside* the file (changelog for docs, `schema_version` for
  JSON), not in the filename. Git holds the history.
- Runtime data lives under the repo's existing `res/` — `res/config/` for
  committed configuration, `res/library/` for the Resource Library, and
  `res/{inputs,outputs,workdir}/` for transient data.
- Markdown is authored first; HTML is generated from it later, not
  hand-maintained in parallel.
- Update docs every 2–3 confirmed decisions — **or at the end of a working
  session, whichever comes first.** Batching is fine; losing a decision
  because a session ended mid-batch is not.

---

## Where a value is owned

Encode targets appear in more than one place. Ownership resolves it:

| Value | Owner | Everyone else |
|---|---|---|
| Encode targets (codec, bitrate, sample rate) | `shared/requirements/layer0-requirements.md` — TGT-003…008 | cites the ID |
| Behavioural rule text | `shared/requirements/visual-grammar.md` | cites VGR-xx |
| Style tokens | `shared/specs/style-contract.md` | — |
| Runtime contract JSON | `res/config/style/global_style_contract.json` | generated from the spec |

*(Config Mgmt question 5 will settle whether the contract's `output_encode`
block references TGT or duplicates it. Until then, TGT is the owner.)*

---

## Migration-test fixtures

`res/config/style/global_style_contract.json` is a single live filename with
`schema_version` inside. Migration tests need older versions to migrate
*from*, and cannot read git history — so frozen copies belong at
`tests/fixtures/contracts/v1.0.0.json` when the first migration is written.
