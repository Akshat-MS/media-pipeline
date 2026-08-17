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

## Backlog

Phase 1 decisions are recorded in `engine/architecture.md` and have not yet
been extracted into individual records. The eight Config Mgmt design questions
will produce the first new entries.
