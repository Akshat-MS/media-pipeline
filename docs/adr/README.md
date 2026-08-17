# Architecture Decision Records

One file per decision. Append-only — never edit an accepted record; supersede
it with a new one and set the old record's status to `superseded by ADR-NNN`.

IDs are globally sequential across both tracks, so any code comment or
document can cite `ADR-009` unambiguously.

Filename: `ADR-<NNN>-<short-slug>.md`

## Template

```markdown
# ADR-NNN · <title>

Status:   proposed | accepted | superseded by ADR-NNN
Date:     YYYY-MM-DD
Context:  <which task/question this arose from>

## Context
What forces are at play. What made this a decision rather than an obvious call.

## Decision
What we chose, stated plainly.

## Consequences
+ what this makes easier
− what this makes harder or forecloses

## Alternatives rejected
- <option> — why not
```

## Index

| ID | Decision | Origin |
|---|---|---|
| [ADR-001](ADR-001-core-language-and-runtime.md) | Core language and runtime | Phase 1 §1.1 |
| [ADR-002](ADR-002-local-state-store.md) | Local state store | Phase 1 §1.2 |
| [ADR-003](ADR-003-project-structure-and-module-boundaries.md) | Project structure and module boundaries | Phase 1 §1.3 |
| [ADR-004](ADR-004-job-resumability-and-checkpointing.md) | Job resumability and checkpointing | Phase 1 §1.4 |
| [ADR-005](ADR-005-schema-versioning-strategy.md) | Schema versioning strategy | Phase 1 §1.5 |
| [ADR-006](ADR-006-testing-and-local-ci.md) | Testing and local CI infrastructure | Phase 1 §1.7 |

Phase 1 §1.6 (Quality & Validation Thresholds) is not an ADR — it is a
requirements register, at
[`../shared/requirements/quality-thresholds.md`](../shared/requirements/quality-thresholds.md).

**Next:** ADR-007 onward will come from the eight Config Mgmt design questions
in [`../engine/config-mgmt-handoff.md`](../engine/config-mgmt-handoff.md).
