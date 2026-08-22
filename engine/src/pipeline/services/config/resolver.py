"""
Theme resolution for the global style contract.

Implements ADR-007 §2 (resolve once at load, flat token set, default
navy) and §7 (CLI arg > PIPELINE_STYLE_THEME env var > contract's own
theme_selected > navy floor, winning source logged whenever more than one
source is set). resolve_theme() is the only public entrypoint — loader.py
hands it a validated StyleContract, the rest of the pipeline (eventually
Rendering) gets back a flat ResolvedStyleContract with no theme branching
left in it.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pipeline.services.config.models import (
    AnimationDefaults,
    Canvas,
    CodeBlock,
    Footer,
    Lists,
    OutputEncode,
    PaletteRoles,
    StyleContract,
    Table,
    TypeScale,
    TypeStyleAbsolute,
    TypeStyleRelative,
    Verification,
)

logger = logging.getLogger(__name__)

KNOWN_THEMES = ("navy", "blue", "green_dark")
DEFAULT_THEME = "navy"

__all__ = ["ThemeResolutionError", "ResolvedStyleContract", "resolve_theme"]


class ThemeResolutionError(Exception):
    """Raised when a theme name was actually specified (by any source) but
    isn't recognized. Distinct from "nothing specified", which resolves to
    DEFAULT_THEME instead of raising — see ADR-007 §2."""


class ResolvedStyleContract(BaseModel):
    """
    Flat, single-theme, rendering-ready config. No `themes` sub-object
    survives here, no theme branching downstream — Rendering only ever
    sees this shape (ADR-007 §2). Immutable by normal pydantic v2 usage;
    constructed once by resolve_theme() and passed explicitly to whatever
    needs it, never fetched from a global (ADR-007 §6).
    """

    model_config = ConfigDict(extra="forbid")

    # Provenance carried through from the envelope — useful for logs/debugging
    schema_version: str
    source: str
    generated_at: datetime
    theme: str  # which theme actually got resolved

    # Flattened from payload.themes.<theme> — the only fields that vary by theme
    background_base_color: str
    background_accents: list[str]
    text_secondary: str
    text_tertiary: str
    eyebrow: str
    accent_marker: str
    measured_body_contrast: float

    # Everything else from payload — already theme-independent, carried through as-is
    version: str
    canvas: Canvas
    type_scale: TypeScale
    palette_roles: PaletteRoles
    type_styles: dict[str, TypeStyleAbsolute | TypeStyleRelative]
    lists: Lists
    table: Table
    code_block: CodeBlock
    footer: Footer
    animation_defaults: AnimationDefaults
    output_encode: OutputEncode
    required_fonts: list[str]
    verification: Verification
    entity_grammar: str


def _select_theme(contract: StyleContract, *, cli_theme: str | None) -> tuple[str, str]:
    """ADR-007 §7 precedence chain. Returns (theme_name, source_label) —
    source_label is only used for the "which source won" log line."""
    env_theme = os.environ.get("PIPELINE_STYLE_THEME")
    contract_theme = contract.payload.theme_selected

    candidates = [
        ("CLI argument", cli_theme),
        ("PIPELINE_STYLE_THEME env var", env_theme),
        ("contract's theme_selected field", contract_theme),
    ]
    set_candidates = [(label, value) for label, value in candidates if value]

    if not set_candidates:
        return DEFAULT_THEME, "default (navy floor, nothing else set)"

    winner_label, winner_value = set_candidates[0]

    if len(set_candidates) > 1:
        others = ", ".join(f"{label}={value!r}" for label, value in set_candidates[1:])
        logger.info(
            "theme resolved to %r from %s (overriding %s)",
            winner_value,
            winner_label,
            others,
        )

    return winner_value, winner_label


def resolve_theme(contract: StyleContract, *, cli_theme: str | None = None) -> ResolvedStyleContract:
    """
    Resolve which theme applies (ADR-007 §7) and flatten the contract into
    a single, rendering-ready object (ADR-007 §2). An unrecognized theme
    name fails loudly regardless of which source set it — "nothing
    specified" and "something specified but wrong" are different cases.
    """
    theme_name, source_label = _select_theme(contract, cli_theme=cli_theme)

    if theme_name not in KNOWN_THEMES:
        raise ThemeResolutionError(
            f"unknown theme {theme_name!r} (from {source_label}) — expected one of {KNOWN_THEMES}"
        )

    theme = getattr(contract.payload.themes, theme_name)
    payload = contract.payload

    return ResolvedStyleContract(
        schema_version=contract.schema_version,
        source=contract.source,
        generated_at=contract.generated_at,
        theme=theme_name,
        background_base_color=theme.background.base_color,
        background_accents=theme.background.accents,
        text_secondary=theme.text_secondary,
        text_tertiary=theme.text_tertiary,
        eyebrow=theme.eyebrow,
        accent_marker=theme.accent_marker,
        measured_body_contrast=theme.measured_body_contrast,
        version=payload.version,
        canvas=payload.canvas,
        type_scale=payload.type_scale,
        palette_roles=payload.palette_roles,
        type_styles=payload.type_styles,
        lists=payload.lists,
        table=payload.table,
        code_block=payload.code_block,
        footer=payload.footer,
        animation_defaults=payload.animation_defaults,
        output_encode=payload.output_encode,
        required_fonts=payload.required_fonts,
        verification=payload.verification,
        entity_grammar=payload.entity_grammar,
    )
