# ADR-005 · Schema versioning strategy

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.5 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

## Concrete Design

Every persisted artifact schema (job config, checkpoint data, alignment output, stage manifests) carries an explicit `schema_version: str` field using strict semver (`MAJOR.MINOR.PATCH`), placed as the **first key** in every JSON schema for human scannability.

- **MAJOR** bump: breaking change (field removed, type changed, semantic meaning changed) → requires a migration function.
- **MINOR** bump: additive, backward-compatible (new optional field with a default) → no migration needed, just a version bump.
- **PATCH** bump: non-structural (doc/description changes only) → no code impact.
- All schemas start at `1.0.0` on Day 1 — do not skip versioning "because it's early."

**Base template** (every schema inherits this envelope):

schema envelope · base.json

```
{
  "schema_version": "1.0.0",
  "generated_at": "2026-08-12T10:00:00Z",
  "generator": "pipeline.stages.align",
  "data": { }
}
```

**Breaking change policy**: a MAJOR bump requires a corresponding entry in `src/pipeline/models/migrations.py` mapping `(schema_name, from_version) -> migrate_fn`. Old job data on disk is never mutated in place — migrations run at *read* time, producing an in-memory upgraded object.

## Trade-offs & Edge Cases

- **Version field omission** in early hand-written fixtures → enforce via Pydantic model validation (required, no default) so a missing version fails loudly.
- **Over-versioning stage-internal ephemeral data** is wasted ceremony — only version data that persists across a checkpoint boundary or process restart.
- **Migration drift**: write the migration in the same commit as the breaking change, no exceptions.

## Claude Code Implementation Spec

*Spec file: `schema-versioning.py`*
```

# Task: Implement schema versioning envelope and migration framework.


# 1. Create src/pipeline/models/envelope.py:
class SchemaEnvelope(BaseModel):
    schema_version: str  # required, validated against semver regex
    generated_at: datetime
    generator: str
    data: dict


# 2. Add semver validation helper (regex: ^\d+\.\d+\.\d+$) as a Pydantic

#    field_validator on schema_version.


# 3. Create src/pipeline/models/migrations.py:
MIGRATIONS: dict[tuple[str, str], Callable[[dict], dict]] = {}

def register_migration(schema_name: str, from_version: str):
    def decorator(fn):
        MIGRATIONS[(schema_name, from_version)] = fn
        return fn
    return decorator

def migrate_to_latest(schema_name: str, payload: dict) -> dict:
    # applies chained migrations until payload version == CURRENT_VERSION
    ...


# 4. Every stage output model (AlignmentResult, NarrationManifest, RenderManifest)

#    wraps its `data` payload in SchemaEnvelope before writing to disk.


# 5. Add a `pipeline schema check ` CLI command that loads a JSON file,

#    reports its schema_version, and warns if a migration would be applied.
```
