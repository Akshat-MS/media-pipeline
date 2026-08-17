# Delivery Targets

**Register A — TGT-001…011.** Numeric properties of the finished video file,
verified after render.

**Status:** complete (v1).
**Provenance:** derived from competitive analysis of the original lecture, our
previous output, and the competitor's output (measurements via ffprobe /
volumedetect / frame sampling). Evidence is retained in
[`competitive-analysis.md`](competitive-analysis.md).

> **These values are owned here.** Any other document that states a codec,
> bitrate, resolution, sample rate or loudness figure must **cite the TGT id
> rather than repeat the number**. Two copies of a number will drift; a
> citation cannot. See the ownership table in `docs/README.md`.
>
> Known citers: [`quality-thresholds.md`](quality-thresholds.md) (Phase 1
> §1.6) and the `output_encode` block of
> [`../specs/style-contract.md`](../specs/style-contract.md).

---

## Targets

| ID | Property | Target | Owner (pipeline section) | Status |
|---|---|---|---|---|
| TGT-001 | Resolution | 1920x1080 | Rendering & Composing > Video Compose | adopted |
| TGT-002 | Export frame rate | 24–30 fps | Rendering & Composing > Video Compose | adopted |
| TGT-003 | Video codec/profile | H.264 High Profile | Rendering & Composing > Video Compose | adopted |
| TGT-004 | Video bitrate | 8–12 Mbps @ 1080p30 | Rendering & Composing > Video Compose | adopted |
| TGT-005 | Audio codec | AAC | Rendering & Composing > Video Compose | adopted |
| TGT-006 | Audio channels | Stereo | Transcript Alignment > Audio Preprocessing + Video Compose | adopted |
| TGT-007 | Audio sample rate | 48 kHz | Transcript Alignment > Audio Preprocessing *(do not reuse ASR-downsampled copy)* | adopted |
| TGT-008 | Audio bitrate | 192–256 kbps | Rendering & Composing > Video Compose | adopted |
| TGT-009 | Audio mean volume | −18 to −16 dB (~−16 LUFS) | Video Compose (mastering/normalization) | adopted |
| TGT-010 | Audio peak ceiling | −1.0 dB | Video Compose (mastering/normalization) | adopted |
| TGT-011 | Duration | Match full transcript length, no silent trimming | Sequence Mapping + Transcript Alignment | adopted |

**Note on TGT-011:** stated as a rule rather than a number because the target
is relative to each lecture's transcript. It is still post-render checkable,
so it stays in Register A.

---

---

## Machine-readable

Wrapped in `SchemaEnvelope` per Phase 1's `models/envelope.py`.

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "delivery_targets",
  "generated_at": null,
  "source": "layer_0_competitive_analysis",
  "payload": {
    "delivery_targets": [
      {
        "id": "TGT-001",
        "property": "resolution",
        "target": "1920x1080",
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-002",
        "property": "export_fps",
        "target": [
          24,
          30
        ],
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-003",
        "property": "video_codec_profile",
        "target": "h264_high",
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-004",
        "property": "video_bitrate_mbps",
        "target": [
          8,
          12
        ],
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-005",
        "property": "audio_codec",
        "target": "aac",
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-006",
        "property": "audio_channels",
        "target": 2,
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-007",
        "property": "audio_sample_rate_hz",
        "target": 48000,
        "owner": "align.audio_preprocessing",
        "status": "adopted"
      },
      {
        "id": "TGT-008",
        "property": "audio_bitrate_kbps",
        "target": [
          192,
          256
        ],
        "owner": "render.video_compose",
        "status": "adopted"
      },
      {
        "id": "TGT-009",
        "property": "audio_mean_lufs",
        "target": -16,
        "owner": "render.mastering",
        "status": "adopted"
      },
      {
        "id": "TGT-010",
        "property": "audio_peak_ceiling_db",
        "target": -1.0,
        "owner": "render.mastering",
        "status": "adopted"
      },
      {
        "id": "TGT-011",
        "property": "duration",
        "target": "match_transcript_no_trim",
        "owner": "sequence_mapping",
        "status": "adopted"
      }
    ]
  }
}
```

---

## Governance

- IDs are **immutable and append-only**. Never renumber or reuse.
- Retire by `status` (`rejected` / `superseded_by: <ID>`), never by deleting a
  row — a deleted row leaves dangling citations and erases the reasoning.
- Status vocabulary: `adopted`, `constraint`, `proposed`, `rejected`,
  `superseded`.
- Register B descriptions are edited **only** in
  `visual_grammar_requirements.md`.

---
