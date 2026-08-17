# ADR-007 · Config Mgmt

Status:   accepted
Date:     2026-08-17
Context:  Phase 2 — Config Mgmt (the eight design questions in
          `../engine/config-mgmt-handoff.md`, § 3 · Actual Prompt)

> Deliberately kept as a single ADR rather than one per question. Convention
> elsewhere in this repo (ADR-001…006) is one decision per file for clean
> supersession; this component's eight questions were judged closely coupled
> enough to read better together. **Deviation from append-only:** later
> changes to one section (e.g. Q7's precedence chain, if Q2's default
> changes) will edit this file's section in place rather than superseding
> the whole document — each section below is dated so edit history stays
> visible even without a new file per change.

## 1 · Placement & module layout (Q1)

**Decision:** `src/pipeline/services/config/`, flat layout — `loader.py`,
`models.py`, `resolver.py`. Cross-field validation rules live as
`@model_validator`/`@field_validator` methods inside `models.py`, not a
separate `validation.py`.

**Rationale:** Placement was already settled by the Phase 1 scaffold
(peer of `services/resource_library/`). The known validation rules (theme
roles must match across all three themes; specific fields must never be
null) are few enough that pydantic v2's own validator decorators handle
them without a dedicated file. `state/` and `core/` are similarly-sized
flat modules — no precedent in this repo for splitting validation out at
this scale. Re-open only if a future rule needs to reach outside the
contract itself (e.g. filesystem-level font-availability checking, which
is out of scope per Q3/§6 below regardless).

## 2 · Theme resolution (Q2)

**Decision:** Resolve once at load, not on every read. `resolver.py` takes
a validated contract + theme name and returns a flat, fully-resolved token
set — no `navy`/`blue`/`green_dark` branching survives downstream.
**Default theme is `navy`** when no theme is specified at all. An
unrecognized theme name (e.g. a typo) still fails loudly rather than
falling back to navy — "nothing specified" and "something specified but
wrong" are different failure modes and should not collapse into the same
behavior.

**Rationale:** Theme is a once-per-job, CLI-level choice, not something
switched mid-render — Rendering is the only real consumer today, and
resolving once removes an entire class of "wrong theme used somewhere
downstream" bugs. The default's precedence relative to CLI/env is
formalized in Q7.

## 3 · Validation model (Q3)

**Decision:** Every field is required by default. The only structural
nullable fields are `theme_selected` (defaults per Q2) and
`slide_transition.type`. Fields the contract itself declares a fallback
for (e.g. `type_styles.math.fallback`) are parsed through as optional —
Config Mgmt never invents a fallback for a field that doesn't declare one.
Every other field, including every key inside each `themes.*` block, is
mandatory; a missing or wrong-typed field fails at load with the full
field path (e.g. `payload.themes.blue.accent_marker`), not a silent
substitution. No `default.json` / blanket defaulting mechanism.

**Rationale:** The contract is a finished, validated Layer 1 artifact
(`source: "layer_1_manual"`), not a form filled in incrementally — a
missing mandatory field is almost certainly a bug, and silently defaulting
it (especially a theme palette value) produces output that looks
plausible but is quietly wrong, which is harder to catch than an
immediate crash. Font-family fallback is the one legitimate defaulting
case, and the contract already has a mechanism for it. Font *availability*
checking stays out of scope (§6 concern, arguably render-host not config).

## 4 · Schema versioning (Q4)

**Decision:** The contract gets its own envelope-shaped model in
`models.py` mirroring its actual JSON top level (`schema_version`,
`artifact_type`, `generated_at`, `source`, `payload`) rather than being
forced into `SchemaEnvelope`'s literal `generator`/`data` fields.
`artifact_type: "global_style_contract"` serves as the `schema_name` for
`migrations.py`. Nothing gets registered in `migrations.py` yet — at
`1.0.0` there is nothing to migrate from. The loader compares the file's
declared `schema_version` against what `models.py` expects: equal loads
directly, older calls `migrate_to_latest("global_style_contract", ...)`,
which only succeeds once a real migration is registered for that jump.

**Rationale:** `SchemaEnvelope` (ADR-005) is documented as being for *"a
module's actual output content"* — `generator` names a producing pipeline
module. The style contract is hand-authored at design time, not produced
by a pipeline module at runtime; forcing it into that shape would be
semantically wrong even though renaming two fields would technically fit.
`migrations.py`'s actual machinery (`register_migration`,
`get_current_version`, `migrate_to_latest`) only needs a `schema_name`
string and a `schema_version` key — it doesn't require `SchemaEnvelope`
specifically, so the migration chain itself needs no changes.

## 5 · Single source of truth for encode targets (Q5)

**Decision:** `delivery-targets.md` remains the owner of TGT-003…008 (this
was already documented there, and confirmed at project kickoff). The
contract's `output_encode` block keeps its current values as-is — the
loader does not fetch or parse `delivery-targets.md` at runtime. Instead,
one test in the Config Mgmt suite cross-checks `output_encode`'s values
against `delivery-targets.md`'s TGT-003…008 at test time and fails on
drift.

**Rationale:** `delivery-targets.md` already states its own rule ("cite
the TGT id rather than repeat the number") and already lists the
contract's `output_encode` block as a known citer that currently
duplicates rather than purely cites. A runtime cross-file fetch adds a new
failure mode (moved file, parse error) for something that's only a
concern when the two documents actually diverge — which a test catches at
the moment it matters, without runtime coupling.

## 6 · Immutability and access pattern (Q6)

**Decision:** `load_style_contract(path, theme=None) -> ResolvedStyleContract`
is a plain function, called once per job, with the result passed
explicitly to whatever stage needs it. No singleton, no `get_config()`
global lookup, no `@lru_cache`. Immutability falls out of using pydantic
v2 models the normal way (mutation isn't the standard access pattern),
without needing to engineer anything extra for it.

**Rationale:** Matches the only existing precedent for shared load-once
state in this repo — `state/db.py`'s `connect()`, explicitly documented as
*"the single entrypoint every other module should use,"* called once and
threaded through explicitly rather than fetched from a global. A grep of
`src/pipeline` found no singleton/`get_instance()`/`@lru_cache` pattern
anywhere to diverge from.

## 7 · Override precedence (Q7)

**Decision:** Highest to lowest precedence for theme selection:

1. CLI argument (`--theme`, once a job-runner CLI exists)
2. Environment variable — `PIPELINE_STYLE_THEME`
3. Contract's own `theme_selected` field, if set
4. Navy (the Q2 default floor)

`load_style_contract()` logs (not warns) which source won whenever more
than one source is set and they disagree, so an unexpected theme choice is
traceable rather than silently resolved three stages downstream.

**Rationale:** No CLI entrypoint exists in the repo yet, so this is new
ground rather than matching an existing pattern — the env var name follows
the one existing convention (`PIPELINE_DB_PATH` in `db.py`). `navy` from
Q2 is the bottom of this same stack, not a separate rule.

## 8 · Forward fit for Layer 4 / Resource Library (Q8)

**Decision:** Keep the loader style-contract-specific. Do not design a
generic-over-artifact-types loader now.

**Rationale:** The style contract and the future Resource Library differ
on every axis that would make shared genericity worthwhile today: source
(static hand-authored JSON vs. external icon-library lookups per entity),
update cadence (rare vs. frequent), and shape (single document vs. a
growing keyed collection). Layer 4 has no committed schema yet — 
generalizing from one concrete example risks placing the abstraction's
seams where style-contract happens to vary, not where the two artifacts
actually overlap, which can't be seen until Layer 4's real shape exists.
Revisit when Layer 4 ships a real schema; the envelope pattern from Q4 and
the fail-loudly posture from Q3 are the most likely candidates to extract
into something shared at that point.
