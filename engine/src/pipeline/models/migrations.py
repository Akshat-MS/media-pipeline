"""
Migration registry for module-output schemas (per Phase 1, item 1.5).

A schema's "current version" is derived automatically as the highest
to_version seen across all registered migrations for that schema — there
is no separate place to declare it, so it can never drift out of sync with
what's actually registered. Data on disk is never mutated in place;
migrate_to_latest() always operates on an in-memory dict and returns an
upgraded copy.

Deliberately empty of real migrations right now — same pattern as
core/registry.py (Task 6/7): nothing to migrate until a real module exists
with more than one schema version.
"""

from __future__ import annotations

from typing import Callable

MigrateFn = Callable[[dict], dict]

# (schema_name, from_version) -> function that upgrades a payload one step
# forward, bumping its schema_version field in the process.
MIGRATIONS: dict[tuple[str, str], MigrateFn] = {}

# schema_name -> highest to_version registered for it. Kept in sync
# automatically by register_migration — never set directly.
CURRENT_VERSIONS: dict[str, str] = {}


def _parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"not a valid MAJOR.MINOR.PATCH version: {version!r}")
    try:
        a, b, c = (int(p) for p in parts)
    except ValueError:
        raise ValueError(f"not a valid MAJOR.MINOR.PATCH version: {version!r}") from None
    return (a, b, c)


def register_migration(schema_name: str, from_version: str, to_version: str):
    """
    Decorator. The wrapped function must take a payload dict at
    `from_version` and return one at `to_version` (with schema_version
    updated inside the returned dict — this is checked at migration time,
    not registration time).

        @register_migration("visual_manifest", from_version="1.0.0", to_version="1.1.0")
        def _migrate(data: dict) -> dict:
            data["element_type"] = data.pop("shape_type")
            data["schema_version"] = "1.1.0"
            return data
    """

    def decorator(fn: MigrateFn) -> MigrateFn:
        key = (schema_name, from_version)
        if key in MIGRATIONS:
            raise ValueError(
                f"a migration from {from_version!r} is already registered for {schema_name!r}"
            )
        MIGRATIONS[key] = fn

        current = CURRENT_VERSIONS.get(schema_name)
        if current is None or _parse_version(to_version) > _parse_version(current):
            CURRENT_VERSIONS[schema_name] = to_version

        return fn

    return decorator


def get_current_version(schema_name: str) -> str:
    try:
        return CURRENT_VERSIONS[schema_name]
    except KeyError:
        raise KeyError(
            f"no migrations registered for schema {schema_name!r} — "
            "cannot determine its current version"
        ) from None


def migrate_to_latest(schema_name: str, payload: dict) -> dict:
    """
    Apply registered migrations, in order, until payload's schema_version
    reaches the current version for this schema. Returns a new dict — the
    input payload is never mutated.

    Raises rather than guessing whenever something doesn't add up: a
    missing schema_version, a version newer than anything known, a gap in
    the migration chain, or a migration that doesn't actually bump the
    version.
    """
    if "schema_version" not in payload:
        raise ValueError(
            f"payload for schema {schema_name!r} is missing 'schema_version' — cannot migrate"
        )

    current = get_current_version(schema_name)
    version = payload["schema_version"]

    if _parse_version(version) > _parse_version(current):
        raise ValueError(
            f"payload for {schema_name!r} claims version {version}, which is newer than "
            f"the highest known version {current} — this looks like a missing migration "
            "registration, not something safe to guess past"
        )

    payload = dict(payload)  # never mutate the caller's dict
    seen_versions: set[str] = set()

    while version != current:
        if version in seen_versions:
            raise RuntimeError(
                f"migration cycle detected for {schema_name!r} — version {version!r} "
                "was visited twice without reaching the current version"
            )
        seen_versions.add(version)

        key = (schema_name, version)
        if key not in MIGRATIONS:
            raise KeyError(
                f"no migration registered to move {schema_name!r} forward from "
                f"version {version!r} (current is {current!r}) — the migration chain has a gap"
            )

        migrate_fn = MIGRATIONS[key]
        payload = migrate_fn(payload)

        new_version = payload.get("schema_version")
        if new_version == version:
            raise RuntimeError(
                f"migration for {schema_name!r} from {version!r} did not update "
                "schema_version in its returned payload"
            )
        version = new_version

    return payload


def reset_migrations() -> None:
    """Test helper only — clears all registered migrations. Not used by
    application code, same purpose as core.registry.reset_registry()."""
    MIGRATIONS.clear()
    CURRENT_VERSIONS.clear()
