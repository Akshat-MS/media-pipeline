# Config Mgmt — Implementation Handoff

Paste the **Actual Prompt** section into a new chat, with the files listed
under **Inputs** attached.

---

## 1 · Context

### Project
**Lecture Alive AI** — repo `github.com/Akshat-MS/media-pipeline` (public,
tag `phase1-complete`). A local-first pipeline that takes a slide deck (PPTX)
plus a lecture video (MP4) and produces an aligned, animated, narration-synced
output video.

Deliverable set: 5 Operating Systems lecture videos (V017, V018, V028, V029,
V030), each with its own PPTX, sharing one visual identity.

### Two parallel tracks
- **Strategy 1 (automated tool)** — the pipeline itself. Phase 1 foundations
  complete. **Config Mgmt is the next build.**
- **Strategy 2 (prompt-driven)** — produces the client deliverable *and* the
  ground-truth artifacts the tool consumes. Layer 0 and Layer 1 complete.

**Config Mgmt exists because Layer 1 produced a real artifact for it to hold:**
the global style contract. This is not speculative infrastructure — the
contract is finished, validated, and has three theme variants.

### What already exists (Phase 1 — extend, do not redesign)
- Python 3.13, pydantic v2, `src/pipeline/` layout
- `src/pipeline/state/` — SQLite state store (WAL), jobs/job_stages/artifacts
- `src/pipeline/core/` — `stage_protocol.py`, `manifest.py`
  (`StageManifest`/`Artifact`), `registry.py` (`register_stage()`, currently
  empty by design)
- `src/pipeline/orchestrator.py` — fork/join, checkpoint/resume, retry
- `src/pipeline/models/` — `envelope.py` (`SchemaEnvelope`) + `migrations.py`
  (migration chain framework, **nothing registered yet**)
- `src/pipeline/validation/` — `thresholds.py`, `validators.py`, 8 quality
  gates defined
- `src/pipeline/modules/` — **empty**, intentionally
- `tests/` — 78 unit tests, ~96% coverage
- 3 LXD containers: `pipeline-structure`, `pipeline-speech`, `pipeline-render`
  (CPU-only, no GPU)

### Where Config Mgmt sits
It is **not a Stage.** It has no `StageManifest` in/out and does not appear in
`registry.py` or `STAGE_ORDER`. It is infrastructure, like `state/` and
`core/` — every stage reads from it.

**The style contract's JSON artifact is `SchemaEnvelope`'s first real
customer.** The migration chain has been empty since Phase 1; this is what
finally registers something in it.

---

## 1b · Design representation — what is already settled

Only boundaries and data flow are fixed. **Internals are deliberately not
drawn** — module layout, resolution strategy, and access pattern are open
questions 1, 2 and 6, to be decided in discussion.

```
                     DESIGN TIME                    │              RUN TIME
  ───────────────────────────────────────────────── │ ─────────────────────────────────────
                                                    │
   Layer 0  requirements register                   │
      │  TGT-003…008 encode targets                 │
      │  (overlaps contract — see Q5)               │
      ▼                                             │
   Layer 1  global style contract  ──────────────┐  │
      · canvas + grid (12×118, 8×90, 24 gutter)  │  │
      · type scale (base 31, ratio 1.25)         │  │
      · type styles, lists, tables, code, footer │  │
      · palette ROLES + carrying channels        │  │
      · 3 theme variants, theme_selected = null  │  │
      · animation defaults, output encode        │  │
      · NO entity grammar                        │  │
                                                 │  │
   Layer 4  visual vocabulary   (FUTURE)  ─ ─ ─ ─┤  │
      · entity → shape / icon / palette-role     │  │
      · per topic, backs Resource Library        │  │
                                                 ▼  │
   ┌────────────────────────────────────────────────┴──────────────────────┐
   │  CONFIG MGT          src/pipeline/config/   (placement = Q1)          │
   │                                                                        │
   │   load  →  validate  →  version  →  resolve theme  →  serve            │
   │                                                                        │
   │   · NOT a Stage — no StageManifest in/out, not in registry.py          │
   │   · infrastructure, peer of state/ and core/                           │
   │   · theme chosen at RUN time (CLI arg)  ──────────────────────────┐    │
   │   · internal layout / access pattern  =  OPEN (Q1, Q2, Q6)        │    │
   └───────────────┬────────────────────────────────────────────────────┼───┘
                   │ uses                                               │
                   ▼                                                    │
   ┌──────────────────────────────┐                          theme name │
   │ models/envelope.py           │  SchemaEnvelope                     │
   │ models/migrations.py         │  ← FIRST real entry in the          │
   │                              │    migration chain (empty until now)│
   └──────────────────────────────┘                                     │
                                                                        │
   reads from Config Mgt ──────────────────────────────────────────────┘
   ┌──────────────────────────────────────────────────────────────────────┐
   │  renderer  (Phase 5, does not exist yet)                             │
   │  stages via orchestrator.py                                          │
   │  validation/thresholds.py   ← encode targets, if contract owns them  │
   └──────────────────────────────────────────────────────────────────────┘
```

### Settled vs open

| Settled | Open — decide in discussion |
|---|---|
| Not a Stage; not registered in `registry.py` | Module layout inside `config/` (Q1) |
| Infrastructure peer of `state/` and `core/` | Raw contract vs pre-resolved token set (Q2) |
| Holds the Layer 1 global style contract | Access pattern — DI, singleton, orchestrator (Q6) |
| Theme selected at run time, not baked | Where encode targets live (Q5) |
| Uses `SchemaEnvelope` + migration chain | Generic over artifact types now, or later (Q8) |
| Contains no entity grammar | Whether font availability is validated here (§6) |
| Layer 4 vocabulary is a second artifact, later | |

---

## 2 · Inputs to attach

| File | Why |
|---|---|
| `docs/shared/specs/style-contract.md` | **The artifact being managed.** §12 holds the full JSON to load. |
| `docs/shared/requirements/delivery-targets.md` | TGT-001…011 — **the owner** of encode values. See question 5. |
| `docs/shared/requirements/quality-thresholds.md` | Phase 1 §1.6 gates that overlap TGT-003…008 |
| `docs/workflow/playbook.md` | Layer map and the content/presentation/sequence split |
| `docs/shared/specimen/specimen-navy.html` | Reference implementation of the contract; useful for sanity-checking token names |

Repo: state the link, it's public and clonable.

---

## 3 · Actual Prompt

> I'm continuing work on **Lecture Alive AI** (repo:
> `github.com/Akshat-MS/media-pipeline`, tag `phase1-complete`, public —
> please clone and read before we start).
>
> Phase 1 foundations are complete: SQLite state store, Stage contract,
> orchestrator, `SchemaEnvelope` + migration chain, 8 validation gates, 78
> tests at ~96% coverage. `src/pipeline/modules/` is intentionally empty.
>
> **Next task: implement Config Management.**
>
> Config Mgmt loads, validates, versions, and serves the **global style
> contract** — the presentation-layer configuration produced by our design
> process. The finished contract is in the attached
> `docs/shared/specs/style-contract.md` (§12 has the complete JSON).
>
> Key properties of the contract:
> - It carries **canvas/grid, type scale, type styles, palette roles, lists,
>   tables, code block, footer, animation defaults, output encode**.
> - It carries **three theme variants** (`navy`, `blue`, `green_dark`).
>   `theme_selected` is `null` by design — **theme is chosen at runtime**, via
>   CLI argument for the tool and stated explicitly in the prompt workflow.
> - It deliberately contains **no entity grammar** — no shapes, icons, or
>   entity→colour bindings. Those are Layer 4 (visual vocabulary / Resource
>   Library), a separate future artifact.
> - Palette entries are **roles** (`state_a`, `state_b`, `state_c`,
>   `focus_attention`, `warning_error`), not entity assignments. Each role
>   also declares a non-colour carrying channel.
>
> Config Mgmt is **not a Stage** — no `StageManifest` in/out, not registered
> in `registry.py`. It is infrastructure that every stage reads from.
>
> **How we work — please follow this:**
> - Discuss and understand each design decision **before writing code**. No
>   building ahead of confirmed decisions.
> - Flag open questions and trade-offs explicitly rather than silently
>   picking one option.
> - Every piece of code gets **actually run and verified** — real tests,
>   executed, not written and assumed correct — before being handed over.
> - Keep to the existing repo conventions (pydantic v2, existing module
>   layout, existing test style).
>
> **Please start by walking the design questions below — one at a time, with
> trade-offs — before any implementation.** I'll confirm each before we move
> on.
>
> 1. **Placement.** `src/pipeline/config/` as infrastructure alongside
>    `state/` and `core/`, or somewhere else? What's the module layout
>    (`loader.py`, `models.py`, `resolver.py`, …)?
> 2. **Theme resolution.** The contract holds three variants plus
>    theme-independent palette roles. Does Config Mgmt return the raw
>    contract and let callers resolve, or resolve the selected theme once at
>    load and hand back a flat, fully-resolved token set? What happens if an
>    unknown theme name is passed?
> 3. **Validation model.** How closely should pydantic models mirror the JSON
>    structure? Some values are legitimately `null` (`slide_transition.type`,
>    `theme_selected`) and some must never be — how do we express that
>    distinction so a malformed contract fails loudly at load rather than
>    silently at render?
> 4. **Schema versioning.** This is `SchemaEnvelope`'s first real customer
>    and the first entry in the empty migration chain. How do we register
>    `global_style_contract` v1.0.0, and what does the migration path look
>    like when Layer 1 iterates to v2?
> 5. **Single source of truth for encode targets.** The contract's
>    `output_encode` block (codec, bitrate, sample rate) overlaps
>    TGT-003…008 in `docs/shared/requirements/delivery-targets.md`, which are also the
>    basis for gates in `validation/thresholds.py`. Two copies will drift.
>    Which one owns these values, and how does the other reference rather
>    than duplicate them?
> 6. **Immutability and access.** Should the resolved config be frozen after
>    load? What's the access pattern for a stage — dependency injection,
>    module-level singleton, or passed through the orchestrator?
> 7. **Override precedence.** CLI argument vs environment variable vs
>    contract default — what wins, and is anything beyond theme selection
>    overridable at all?
> 8. **Forward fit for Layer 4.** Visual vocabulary (entity → shape/icon/
>    palette-role bindings, per topic, backing the Resource Library) is a
>    second config artifact arriving later. Do we design the loader to be
>    generic over artifact types now, or keep it style-contract-specific and
>    generalise when Layer 4 actually exists?
>
> Once we've settled these, implement, run the tests, and show me real
> output — not assumed-correct code.

---

## 4 · Output format expected

### Code
- `src/pipeline/config/` — module layout agreed in question 1
- pydantic v2 models mirroring the contract
- The contract JSON committed to the repo at an agreed path
  — already extracted to `res/config/style/global_style_contract.json`, single filename with `schema_version` inside
- A registered migration-chain entry for `global_style_contract` v1.0.0

### Tests
- Loads a valid contract successfully
- Rejects a malformed contract loudly at load time
- Resolves each of the three themes correctly
- Rejects an unknown theme name
- Theme-independent palette roles are identical across all three themes
- Envelope version mismatch is handled per the agreed migration behaviour
- Matching the existing suite's style and coverage bar (~96%)

### Verification required
Tests **executed**, with output shown — not written and assumed correct.
Loading the real v3 contract must be part of that run, not a synthetic
fixture only.

### Docs
Per `docs/README.md`:
- Each of the 8 design questions that produces a real decision gets an **ADR**
  in `docs/adr/` (see `docs/adr/README.md` for the template and numbering).
- Update `docs/engine/architecture.md` with the resulting architecture, and
  link the ADRs rather than restating them.
- Update every 2–3 confirmed decisions, or at the end of the session —
  whichever comes first.

**Migration-test fixtures:** the live contract is a single filename with
`schema_version` inside. Migration tests need older versions to migrate
*from* and cannot read git history, so frozen copies belong at
`tests/fixtures/contracts/v1.0.0.json`.

---

## 5 · Explicitly out of scope

| Item | Belongs to |
|---|---|
| Entity grammar — shapes, icons, entity→colour bindings | Layer 4 / Resource Library |
| Rendering anything | Phase 5 |
| Reading PPTX or audio | `asset_deconstructor` / Transcript Alignment |
| Registering a Stage in `registry.py` | Config Mgmt is not a Stage |
| Sequencing, timing, beats | Layer 6 |

---

## 6 · Known context worth carrying over

- **Fonts:** the contract requires Space Grotesk, Inter, Space Mono, and
  Source Serif 4. TTFs are bundled in `docs/shared/specimen/fonts/`. Whether
  Config Mgmt should validate font availability at load is worth raising —
  it's arguably a render-host concern, not a config concern.
- **`warning_error` colour:** `#FF6B6B` is retained despite being
  indistinguishable from `state_a` under deuteranopia (1.01:1). An HSV search
  found no viable alternative (red/pink ceiling 1.19:1). The triangle-icon
  channel is what carries the distinction, and it is **mandatory**. Config
  Mgmt should not "fix" this colour.
- **Nothing consumes this config yet.** The renderer doesn't exist. That's
  accepted — the contract is real and finished, and building the loader now
  means Layer 4 and the renderer arrive to a working config layer rather than
  an empty one.

---

## 7 · Still open elsewhere (not this task)

Carrying these so they aren't lost:

- `asset_deconstructor` design ~60% complete — steps 2.2 (tree granularity)
  and 2.4 (asset isolation + **stable element IDs**) still open. 2.4 is now
  more constrained: Layer 6 beats reference `element_id`, so IDs must be
  stable across re-runs.
- VGR-06 (text-render QC) and VGR-07 (content coverage) owe real entries in
  `thresholds.py` / `validators.py`.
- DEC-001: forced alignment (WhisperX or similar) is required for word-level
  timestamps and **does not exist in the Phase 1 build or the roadmap** —
  an unbudgeted component in Transcript Alignment.
- Both tracks are blocked on the real **V028 `.pptx`** and its audio extract.
