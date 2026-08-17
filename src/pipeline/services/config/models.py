"""
Pydantic model tree for the global style contract
(res/config/style/global_style_contract.json).

Implements ADR-007 §3 (validation model) and §4 (schema versioning) —
see docs/adr/ADR-007-config-mgmt.md for the reasoning behind every
decision encoded here. In short:

- Every field is required by default. A missing or wrong-typed mandatory
  field must fail loudly at load, with a field path pydantic derives
  automatically — not be silently defaulted.
- The only nullable fields are `theme_selected` (resolved by loader.py /
  resolver.py per ADR-007 §2, §7) and `slide_transition.type` /
  `slide_transition.duration_s`.
- A field the contract itself declares a fallback for (`type_styles.math`)
  is parsed through as optional. Config Mgmt never invents a fallback for
  a field that doesn't declare one.
- `StyleContract` mirrors the contract's own top-level envelope
  (schema_version / artifact_type / generated_at / source / payload)
  rather than being forced into `pipeline.models.envelope.SchemaEnvelope`,
  which is documented as being for pipeline-module output, not a
  hand-authored design artifact — see ADR-007 §4 for why that distinction
  matters here.
- `model_config = ConfigDict(extra="forbid")` on every model (via
  `_StrictModel`): an unexpected/misspelled field is itself a form of
  malformed input, and should fail the same way a missing one does.

NOTE — three heterogeneity findings from the real committed contract,
worth revisiting if the contract's shape changes (flagged during
implementation, 2026-08-17, not previously surfaced in the Q1–Q8
discussion):

1. `type_styles` entries have two distinct shapes. 16 of 17 use absolute
   pixel sizing (`step` + `size_px`); `math_subscript` alone uses relative
   em sizing (`size_em` + `vertical_align_em`). Modeled as a
   `TypeStyleAbsolute | TypeStyleRelative` union — pydantic v2 matches
   each dict against whichever variant actually validates.
2. `palette_roles.channels` entries carry either `redundant` or
   `primary_channel`, never both, never neither (the "neither" case would
   defeat the deuteranopia collision guarantee described in
   `palette_roles.collision_warning`). Modeled as one shared model with
   both fields optional plus a validator requiring at least one.
3. `lists.level_1/2/3` are not uniform: `level_2` has an extra
   `stroke_px` (hollow marker), `level_3`'s `size_px` is a `[length, gap]`
   pair rather than a single int (dash marker), not present on the other
   two. Modeled as three distinct named models — same treatment as
   `themes.navy/blue/green_dark` — since these are three fixed, known
   keys, not an open/arbitrary dict.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from pipeline.models.envelope import SEMVER_PATTERN

__all__ = ["StyleContract", "StyleContractPayload", "EXPECTED_SCHEMA_VERSION"]

# The only schema_version this code currently understands directly.
# loader.py loads a file at this version as-is; anything older goes
# through pipeline.models.migrations first (ADR-007 §4). Bump this only
# alongside adding a real @register_migration entry for the jump.
EXPECTED_SCHEMA_VERSION = "1.0.0"


class _StrictModel(BaseModel):
    """Shared base: reject unexpected fields rather than silently ignoring
    them — a stray/misspelled key is a malformed-contract case too."""

    model_config = ConfigDict(extra="forbid")


# ── Canvas ───────────────────────────────────────────────────────────────


class SafeMargin(_StrictModel):
    top: int
    right: int
    bottom: int
    left: int


class ContentArea(_StrictModel):
    width: int
    height: int


class Grid(_StrictModel):
    columns: int
    column_width_px: int
    rows: int
    row_height_px: int
    gutter_px: int
    content_area: ContentArea
    col_origin_fn: str
    row_origin_fn: str
    span_fn: str
    note: str


class Canvas(_StrictModel):
    width: int
    height: int
    fps: int
    safe_margin: SafeMargin
    spacing_base_unit_px: int
    grid: Grid
    satisfies: list[str]  # TGT ids — see ADR-007 §5, delivery-targets.md owns the values


class TypeScale(_StrictModel):
    base_px: int
    ratio: float


# ── Themes ───────────────────────────────────────────────────────────────


class ThemeBackground(_StrictModel):
    base_color: str
    accents: list[str]


class Theme(_StrictModel):
    background: ThemeBackground
    text_secondary: str
    text_tertiary: str
    eyebrow: str
    accent_marker: str
    measured_body_contrast: float


class Themes(_StrictModel):
    """Exactly the three known theme variants — named fields, not a generic
    dict, so a missing theme block fails with a clear path
    (payload.themes.blue) rather than silently being absent."""

    navy: Theme
    blue: Theme
    green_dark: Theme


# ── Palette roles ────────────────────────────────────────────────────────


class PaletteChannel(_StrictModel):
    colour: str
    redundant: str | None = None
    primary_channel: str | None = None

    @model_validator(mode="after")
    def require_one_non_colour_channel(self) -> "PaletteChannel":
        if self.redundant is None and self.primary_channel is None:
            raise ValueError(
                "a palette channel must declare either 'redundant' or "
                "'primary_channel' — colour must never be the only signal "
                "(see palette_roles.collision_warning)"
            )
        return self


class PaletteRoles(_StrictModel):
    text_primary: str
    neutral_structure: str
    state_a: str
    state_b: str
    state_c: str
    focus_attention: str
    warning_error: str
    channels: dict[str, PaletteChannel]
    rule: str
    note: str
    collision_warning: str


# ── Type styles ──────────────────────────────────────────────────────────


class TypeStyleAbsolute(_StrictModel):
    """16 of 17 type_styles entries: absolute pixel sizing off the type
    scale's `step`. family/weight/step/size_px are the real common
    denominator across every entry of this shape; everything else varies
    entry-to-entry in the real contract, hence optional."""

    family: str
    weight: int
    step: int
    size_px: int
    line_height: float | None = None
    tracking: str | None = None
    transform: str | None = None
    colour_role: str | None = None
    fallback: str | None = None  # only "math" declares one — never invented if absent
    style: str | None = None  # only "math_variable" — italic, alongside absolute sizing


class TypeStyleRelative(_StrictModel):
    """math_subscript only: sized relative to its parent (em), not in
    absolute pixels."""

    family: str
    weight: int
    size_em: float
    vertical_align_em: float
    style: str | None = None


# ── Lists ────────────────────────────────────────────────────────────────


class ListLevel1(_StrictModel):
    marker: str
    size_px: int
    indent_px: int
    gap_px: int
    text_style: str
    vertical_gap_px: int


class ListLevel2(_StrictModel):
    marker: str
    size_px: int
    stroke_px: int
    indent_px: int
    gap_px: int
    text_style: str
    vertical_gap_px: int


class ListLevel3(_StrictModel):
    marker: str
    size_px: list[int]
    indent_px: int
    gap_px: int
    text_style: str
    vertical_gap_px: int


class Lists(_StrictModel):
    level_1: ListLevel1
    level_2: ListLevel2
    level_3: ListLevel3


# ── Table / code block / footer ─────────────────────────────────────────


class Table(_StrictModel):
    border: str
    cell_padding: str
    header_fill: str
    rowhead_fill: str
    zebra_striping: bool
    alignment_numeric: str


class CodeBlock(_StrictModel):
    background: str
    border_left: str
    border_left_role: str
    padding: str
    radius_px: int


class Footer(_StrictModel):
    layout: str
    baseline_px: int
    rule: str
    rule_offset_px: int
    slots: list[str]
    colour: str


# ── Animation defaults ───────────────────────────────────────────────────
# Five fixed, named sub-sections with genuinely different shapes by design
# — not heterogeneity to paper over, just five distinct concepts.


class Reveal(_StrictModel):
    duration_s: float
    easing: str
    stagger_s: float
    variants: list[str]


class StateMotion(_StrictModel):
    duration_s: float
    variants: list[str]
    usage_rule: str
    satisfies: list[str]


class Camera(_StrictModel):
    duration_s: float
    easing: str
    variants: list[str]
    rules: list[str]
    satisfies: list[str]


class Layering(_StrictModel):
    rule: str
    satisfies: list[str]


class SlideTransition(_StrictModel):
    """Both fields nullable by design — no transition has been chosen yet.
    Per ADR-007 §3, what "no transition" resolves to at render time is
    still an open follow-up, not decided here."""

    type: str | None = None
    duration_s: float | None = None


class AnimationDefaults(_StrictModel):
    reveal: Reveal
    state_motion: StateMotion
    camera: Camera
    layering: Layering
    slide_transition: SlideTransition


# ── Output encode ────────────────────────────────────────────────────────


class OutputEncode(_StrictModel):
    """Values owned by delivery-targets.md (ADR-007 §5) — kept as-is here,
    cross-checked against that file by a test, not at load time."""

    video_codec: str
    video_bitrate_mbps: list[int]
    audio_codec: str
    audio_channels: int
    audio_sample_rate: int
    audio_bitrate_kbps: list[int]
    satisfies: list[str]  # TGT ids this block claims to satisfy

    @field_validator("video_bitrate_mbps", "audio_bitrate_kbps")
    @classmethod
    def must_be_a_min_max_pair(cls, value: list[int]) -> list[int]:
        if len(value) != 2:
            raise ValueError(f"expected a [min, max] pair, got {value!r}")
        return value


class Verification(_StrictModel):
    contrast_measured: bool
    colourblind_checked: bool
    typography_legibility_verified_fullscreen: bool


# ── Payload + top-level envelope ────────────────────────────────────────


class StyleContractPayload(_StrictModel):
    version: str
    theme_selected: str | None = None  # resolved per ADR-007 §2, §7 — null is expected pre-resolution
    canvas: Canvas
    type_scale: TypeScale
    themes: Themes
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
    entity_grammar: str  # placeholder text today — Layer 4 owns this, per ADR-007 §8


class StyleContract(_StrictModel):
    """
    Mirrors the contract's actual top-level shape — deliberately NOT
    `pipeline.models.envelope.SchemaEnvelope` (see module docstring and
    ADR-007 §4). `artifact_type` doubles as the `schema_name` key used by
    `pipeline.models.migrations`.
    """

    schema_version: str
    artifact_type: Literal["global_style_contract"]
    generated_at: datetime
    source: str
    payload: StyleContractPayload

    @field_validator("schema_version")
    @classmethod
    def validate_semver(cls, value: str) -> str:
        if not SEMVER_PATTERN.match(value):
            raise ValueError(
                f"schema_version must be strict MAJOR.MINOR.PATCH semver, got {value!r}"
            )
        return value
