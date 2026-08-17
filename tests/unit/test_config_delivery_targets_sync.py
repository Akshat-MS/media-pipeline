"""
Drift-detection test for ADR-007 §5: delivery-targets.md owns TGT-003…008;
the contract's output_encode block cites them via 'satisfies' but also
repeats the raw numbers (the JSON's own known-citer duplication, flagged
in delivery-targets.md itself). Rather than couple loader.py to reading
delivery-targets.md at runtime, this single test catches the moment the
two documents actually diverge.
"""

import json
import re
from pathlib import Path

import pytest

from tests.conftest import CONTRACT_PATH

DELIVERY_TARGETS_PATH = (
    CONTRACT_PATH.parents[3] / "docs" / "shared" / "requirements" / "delivery-targets.md"
)

# Maps each cited TGT id to the field in the contract's output_encode
# block it corresponds to, and the property name in delivery-targets.md's
# machine-readable block used to look up the owned value.
TGT_TO_OUTPUT_ENCODE_FIELD = {
    "TGT-003": ("video_codec", "video_codec_profile"),
    "TGT-004": ("video_bitrate_mbps", "video_bitrate_mbps"),
    "TGT-005": ("audio_codec", "audio_codec"),
    "TGT-006": ("audio_channels", "audio_channels"),
    "TGT-007": ("audio_sample_rate", "audio_sample_rate_hz"),
    "TGT-008": ("audio_bitrate_kbps", "audio_bitrate_kbps"),
}


def _load_delivery_targets() -> dict:
    """Extract the fenced ```json machine-readable block from
    delivery-targets.md and parse it — this is the SchemaEnvelope-wrapped
    register described in that file's own '## Machine-readable' section."""
    text = DELIVERY_TARGETS_PATH.read_text()
    heading_idx = text.find("## Machine-readable")
    assert heading_idx != -1, "delivery-targets.md has no '## Machine-readable' section"
    match = re.search(r"```json\n(.*?)\n```", text[heading_idx:], re.DOTALL)
    assert match, "could not find the machine-readable JSON fence in delivery-targets.md"
    envelope = json.loads(match.group(1))
    return {t["id"]: t["target"] for t in envelope["payload"]["delivery_targets"]}


@pytest.fixture(scope="module")
def delivery_targets() -> dict:
    return _load_delivery_targets()


def test_delivery_targets_file_exists_and_has_all_cited_ids(delivery_targets):
    for tgt_id in TGT_TO_OUTPUT_ENCODE_FIELD:
        assert tgt_id in delivery_targets, f"{tgt_id} missing from delivery-targets.md"


@pytest.mark.parametrize("tgt_id", list(TGT_TO_OUTPUT_ENCODE_FIELD))
def test_output_encode_value_matches_owned_delivery_target(real_contract_raw, delivery_targets, tgt_id):
    contract_field, delivery_targets_property = TGT_TO_OUTPUT_ENCODE_FIELD[tgt_id]

    contract_value = real_contract_raw["payload"]["output_encode"][contract_field]
    owned_value = delivery_targets[tgt_id]

    assert contract_value == owned_value, (
        f"output_encode.{contract_field} = {contract_value!r} no longer matches "
        f"{tgt_id}'s owned value ({owned_value!r}) in delivery-targets.md — "
        f"per ADR-007 §5, delivery-targets.md owns this number; update the "
        f"contract to match rather than editing this test."
    )


def test_output_encode_satisfies_list_matches_the_mapping(real_contract_raw):
    """The contract's own 'satisfies' array should be exactly the six IDs
    this test knows how to check — if someone adds a 7th citation there,
    this test should be extended to cover it too, not silently miss it."""
    cited = set(real_contract_raw["payload"]["output_encode"]["satisfies"])
    checked = set(TGT_TO_OUTPUT_ENCODE_FIELD)
    assert cited == checked, (
        f"output_encode.satisfies cites {cited - checked or 'nothing new'} that this "
        f"drift test doesn't check yet — extend TGT_TO_OUTPUT_ENCODE_FIELD"
    )
