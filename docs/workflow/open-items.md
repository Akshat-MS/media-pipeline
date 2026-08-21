# Open Items

**Inbox for observations needing human action.** Append-only.

| | |
|---|---|
| **What belongs here** | Process- and design-level observations — something is missing, contradictory, or unowned |
| **What does not** | Content-level findings about a specific slide or video. Those go in that prompt's own `UNRESOLVED / ASSUMPTIONS / FLAGS` output and are read by the next layer |
| **The test** | Does the next prompt need this, or does a human need to act on it? |

**Promotion path.** This file is an inbox, not a register. When an observation
turns out to be a real requirement, it **graduates to a TGT / VGR / RC id** in
the Layer 1 registers, and the OBS row is closed with a pointer to that id.

**Governance.** OBS ids are immutable and append-only. Close by `status`, never
by deleting a row.

**Status vocabulary:** `open` · `promoted → <ID>` · `fixed` · `rejected` · `deferred`

---

## Layer 1 — Target Spec

Found by running the Layer 1 review checks (`1-target-spec.md` §4) against the
delivered registers.

| ID | Observation | Action needed | Blocks | Priority | Status |
|---|---|---|---|---|---|
| OBS-001 | **RC-001 (Root Cause finding: internal render fps ≠ export fps) had no gate.** Nothing detected an 8 fps internal render upsampled to 30 fps on export — so the worst defect in the competitive analysis passed every check | Two new Delivery Targets added: TGT-012 (configured frame generation rate, gate) and TGT-013 (effective unique frames per second, advisory). RC-001 amended to cite them | — | — | **closed — promoted → TGT-012, TGT-013** |
| OBS-002 | **VGR-06 and VGR-07 are marked `needs_validation_gate: true` with no implementation.** No entries in `thresholds.py` / `validators.py` | Decide whether these are gates or advisory, then implement. Layer 8 is the first layer producing something they could check | Layer 8 | **High** | open |
| OBS-003 | **DEC-001 (Open Decision: word-timestamp source) was open**, while Layers 4, 7 and 8 all already assumed path A (clean the original recording + forced alignment) | **Closed.** Path A confirmed; forced alignment registered as a required component of Transcript Alignment. Layer 4 emits word timings for the whole transcript; Layer 8 selects the phrase span. See closure note below | — | — | **closed — DEC-001 resolved** |
| OBS-004 | **PROP-001 (Proposal: seconds-per-concept metric) has a `null` threshold**, pending a measurement never taken | **Rejected.** Its origin observation compared a full lecture against two trimmed demo samples, and the concern it guards against is structurally precluded by the narration invariant plus TGT-011. See closure note below | — | — | **closed — rejected** |

---

## Layer 2 — Global Theme

Raised during review of the delivered style contract (v3). Recorded here so they
are not lost; **not yet actioned.**

| ID | Observation | Action needed | Blocks | Priority | Status |
|---|---|---|---|---|---|
| OBS-005 | **Palette roles are named `state_a` / `state_b` / `state_c`** — names that carry no meaning. The Layer 2 prompt asked for a semantic role named per colour ("this colour always means blocked/waiting"); the output satisfies the words and loses the intent. Nothing now prevents the same colour meaning different things in different videos | Rename to semantic roles before Layer 6 binds entities to them | Layer 6 | **High** | open |
| OBS-006 | **Style contract version mismatch.** The document says v3; the shipped JSON payload says `"version": "v1"` | Reconcile and decide which is authoritative | Layer 6, Layer 8 | **High** | open |
| OBS-007 | **The `pacing` block was dropped.** The earlier contract carried `fixed_sleeps_allowed: false`, `min_gap_between_actions_s`, `dead_air_defect_threshold_s`. None survive in v3 | Restore, or record deliberately why pacing moved elsewhere | Layer 8 | **High** | open |
| OBS-008 | **Animation durations are fixed constants** (reveal 0.3s, camera 0.8s, state motion 1.1s) with no floor and no compression rule. A fixed duration is a fixed sleep — it conflicts with VGR-05 and RC-002 | Express as defaults compressible to the narration window, with a stated floor | Layer 8 | **High** | open |
| OBS-009 | **The redundant colour channel only works for connectors.** `state_a/b/c` are backed by `line_style: dashed/solid/dotted`, which does not exist on a filled shape — so for nodes, "colour never carries meaning alone" has no second channel | Define a per-shape-class channel map (connector → line style; node → border/fill; label → icon) | Layer 6 | Medium | open |
| OBS-010 | **`token_travel` lost its direction semantics.** The earlier contract defined request = process→resource = "waiting" and assignment = resource→process = "granted". Now it is a bare variant name | Restore the semantics in Layer 6, where entity binding happens | Layer 6 | Medium | open |
| OBS-011 | **`theme_selected` is `null` by design** (runtime parameter), leaving it unclear which theme Layer 6 bindings must be validated against | **Resolved by ADR-007 §2 and §7.** Default is `navy`; precedence is CLI arg → `PIPELINE_STYLE_THEME` → `theme_selected` → navy floor, with the winning source logged. An unknown theme name fails loudly rather than falling back. Layer 6 validates against navy as the default | — | — | **closed — ADR-007 §2, §7** |
| OBS-012 | **Grid vertical arithmetic is unstated.** The contract asserts `8×90 + 7×24 = 888 ✓` without relating 888 to the 932px between margins. **Verified against the specimen — it does reconcile:** 888 grid + 22 clearance + 22 footer-rule-to-baseline = 932. Documentation only; nothing is wrong | Add the reconciliation table to the contract | — | Low | **documentation only** |

---

## Project / documentation

| ID | Observation | Action needed | Blocks | Priority | Status |
|---|---|---|---|---|---|
| OBS-013 | **No artifact validates against `SchemaEnvelope`.** The code expects `schema_version, generated_at, generator, data`; every artifact uses `schema_version, artifact_type, generated_at, source, payload`. **Narrowed by ADR-007 §4**, which rules that the style contract gets its own envelope-shaped model rather than being forced into `SchemaEnvelope` — because `SchemaEnvelope` is for a *module's runtime output* and the contract is hand-authored at design time. That resolves the contract's case and gives a general rule | Apply the same rule to the Layer 1 registers and to future manifests: decide per artifact whether it is a runtime module output (`SchemaEnvelope`) or a hand-authored design artifact (its own model). Do it before Layer 3 produces manifests at scale | Layer 3 onward | **High** | open — narrowed |
| OBS-014 | **The migration chain is empty.** `MIGRATIONS = {}`, so `migrate_to_latest()` raises for any schema. **Reframed:** ADR-007 §4 states this is deliberate — at `1.0.0` there is nothing to migrate *from*, and `loader.py` only calls `migrate_to_latest()` when the file's declared version differs from what the code expects. The rule was not violated | The remaining question is narrower: contract v1→v3 added the grid, `channels` and the `math` styles — a genuine key-set change. Decide whether that should have bumped `schema_version`, and if so, register the migration | Nothing immediately | Medium | open — reframed |
| OBS-015 | **Three documents cite an ownership table in `docs/README.md` that does not exist** (verified — no "owner" string anywhere in that file). The README is also partly stale: three listed files are absent (`1-media-pipeline-foundation.html`, `architecture.svg`, `pipeline_flow.svg`) and two moved into `engine/` | Write the ownership table, or repoint the citations. Refresh the file list | Nothing; erodes the one-owner rule | Medium | open |
| OBS-016 | **A second routing table exists in `competitive-analysis.md`** using the old layer numbering (Layer 1A / 1B / Layer A / Layer 3-as-sequence), contradicting this playbook | Delete it — the prompt owns its own input scope | Risk of mis-scoping a prompt | Medium | open |
| OBS-017 | **Encode values were duplicated across five places.** **Narrowed by ADR-007 §5 + `test_config_delivery_targets_sync.py`**, which parses the machine-readable block of `delivery-targets.md` and asserts the contract's `output_encode` matches per TGT id — with a guard test that fails if a seventh citation is added without extending the check. The contract↔register edge is now automatic. **Still duplicated:** `quality-thresholds.md`, `src/pipeline/validation/thresholds.py` (`DEFAULT_THRESHOLDS`), and `style-contract.md` §10 prose | Extend the same drift-test approach to `thresholds.py`, or make it read the register. `quality-thresholds.md` already flags this as unsettled ("design question 5 will settle whether these reference TGT") — ADR-007 §5 answered it for the contract only | Nothing; guarantees future drift | Medium | open — narrowed |
| OBS-023 | **The palette has six roles, and that number was a starting guess.** It was never checked against the material. Every role beyond what is needed costs contrast headroom and colour-vision separation — and the deuteranopia collision found in contract v3 is exactly the symptom of an over-specified palette | Count the maximum simultaneous states that must be distinguished on the busiest slide across all five decks, then lock the role count | Layer 6 | Medium | open |
| OBS-024 | **Slide transitions sit in the theme layer as an animation default, but arguably belong to sequencing.** Left there because they are global and content-independent; the values are `null` and deferred | Revisit once one slide has run end-to-end. If per-slide variation turns out to be wanted, they move to Layer 8 | Layer 8 | Low | open |
| OBS-027 | **`asset-deconstructor-schema.md` §8 no longer matches Layer 3's output.** The spec is the declared owner of the per-asset shape, but Layer 3 v4 adds `lines[]`, `flags[]`, `labels_prior`, `realizes_prior` and the deck-level wrapper — none of which the spec lists. Two owners of one shape, disagreeing | Fold the new fields into the spec §8, or record in the spec that the layer file extends it and how | Layer 3 output being trusted as spec-conformant | **High** | open |
| OBS-028 | **The merged V017 slide 2 has no background, footer band or logo.** It was reconstructed from a video frame, so it carries none of the deck's chrome. Confirmed by render: it appears on white while every other slide is teal | Add the deck's chrome to that slide in PowerPoint. Otherwise Layer 3's `chrome_pattern` sees slide 2 as an exception, and Layer 5 has no footer to lay out around | Layer 3 chrome consistency | Medium | open |
| OBS-029 | **`mpk deck merge` copies the shape tree but does not re-link images or theme parts.** For the V017 merge this was harmless (the source slide had no pictures), but a source slide with images would lose them silently | Either re-link parts properly, or keep the guard: always `mpk deck render` after a merge and check by eye. The command prints this warning today | Any future merge involving pictures | Medium | open |
| OBS-030 | **`mpk transcript build` has never actually run.** Whisper models download from Hugging Face on first use, and that is blocked in the environment where the command was written — so the code path, arguments and error handling are verified but the model has never loaded. Everything downstream of it (`export` in all four formats, `check`, the review page) is tested against a realistic hand-built transcript | Run once on V017: **64 segments, 1 h 03 m of audio, word timings present**. It did fail — see OBS-032 — and the fix is in. Real counts now recorded in the layer file | Layer 4's first real run | **High** | **closed** — ran on V017, one defect found and fixed |
| OBS-031 | **The Whisper model tier is not chosen, and word-error rate has never been measured.** `--model small` is a default, not a decision. `quality-thresholds.md` sets an advisory ≤12% WER on a reference sample, and `jiwer` is already a project dependency — but nothing uses it, so there is no number | Transcribe one segment set at `small` and `medium`, measure both with `jiwer` against a hand-corrected reference, then fix the tier. Notation-dense segments should be weighted separately (OBS-021) | Confidence in every transcript | Medium | open |
| OBS-032 | **Notation detection was hardcoded to one deck's vocabulary and silently found nothing.** The first real V017 run flagged **0 of 64** segments as notation-bearing, in a transcript that says *semaphore* 8×, *mutex* 7×, *empty* 21× and *BUFSIZE* once. The regex hunted P₁/Rⱼ/{…}/≤ — deadlock vocabulary — while V017 is bounded buffer. A detector that reports zero is worse than no detector: it reads as "nothing to check" | Fixed. `--terms-from MANIFEST` drives detection from Layer 3's `entity_inventory`, unioned with `--vocab`; matching tolerates recogniser mangling (*BUFSIZE* → *"buff size"*). V017 now flags **38 of 64**. `mpk transcript reflag` re-applies without re-transcribing. **Deck terms alone were not enough** — they gave 3 terms and still 0 matches, because *semaphore* and *mutex* are spoken but never drawn; the union is what works | OBS-021, and every notation check | **High** | **closed** — fix in `mpk`, layer file updated |
| OBS-033 | **A comparison operator is missing from slide 5's right-hand annotation.** `v017_s05_104` reads *"Checks number of full slots  in buffer. If  0, waits"* — two spaces where an operator belongs. Its mirror on `v017_s05_103` reads *"If **>** 0, adds to buffer"*. A single character has been lost from a slide about semaphore conditions, and it is invisible to anything that does not compare the two panels | **Not corrected** — VGR-01 keeps the text verbatim, and guessing `==` or `<=` into an educational artifact is worse than showing one is missing. Flagged `possible_lost_operator`, severity error. Settle it against the original deck or the narration, then fix the deck itself, not the manifest | Layer 5 and Layer 8 both read this line; a wrong operator reaches the screen | **High** | open |
| OBS-034 | **Layer 3's fresh-chat verification is still owed.** The V017 manifest was produced in the same session that authored the Layer 3 prompt, which already knew about the slide-2 chrome gap and the oversized code text. The manifest is usable; it is not evidence that the prompt finds those things unaided | Re-run the Layer 3 prompt in a fresh chat on the same `v017.raw.json` and compare. Cheap — one prompt, one paste. Deliberately deferred to keep the end-to-end path moving | Confidence in Layer 3 for V018, V028, V029, V030 | Medium | open — deferred by decision |
| PROP-002 | **A standard intro and outro for every lecture.** V017's highest-scoring picture change (160.15 at 00:00.75) and its last (57.01 at 07:51.25) are both fades, not slide turns. Every video will have them, and today each one is bare. A shared opening — institute or company name — and a closing thank-you followed by the same name would make the set look like a series rather than five separate exports | Build once as a fixed clip pair and concatenate onto every finished video. **Deliberately last**: it touches no layer's logic, costs nothing to defer, and cannot block anything upstream. Note for Layer 9: once it exists, the first and last picture changes in every video are known-not-slide-changes | Perceived polish across the set; TGT-011 duration must account for the added seconds | Low | open — accepted, scheduled last |
| OBS-035 | **The slide-change tier was calibrated on one video.** `mpk video slidechanges` tiers an event strong or weak by how much of the picture moved. On V017 a **confirmed** slide turn scored 17.00 while the opening fade — not a slide change — scored 160.15. Magnitude does not rank significance, and the first threshold (20.0) would have filed a real slide turn as weak | Threshold lowered to 15.0, set below the lowest confirmed real change. `tier_meaning` and `threshold_provenance` now say plainly in the output that tier is not a verdict. **One video is thin evidence for a constant** — re-check against V018's confirmed changes before trusting the default | Every video's slide windows, and therefore every beat in Layer 8 | Medium | open — provisional value, needs a second video |
| OBS-036 | **Deck slides 1 and 2 never appear in the source video *as rendered*.** Matching every deck slide against every second of V017: slides 3, 4 and 5 correlate at **0.996**; slides 1 and 2 peak at **0.495** and **0.527**. **Both have benign explanations, confirmed by manual review:** the video's title card is a white minimal card while deck slide 1 is the purple themed one — same text, different styling; and deck slide 2 *is* the reconstruction of the video's composition **with the professor removed**, so the 0.527 is the presenter's absence, not missing content | **No action. Recorded because the low scores look alarming and are not.** An earlier reading of this row claimed the 66-second recap needed visuals built from scratch — wrong: deck slide 2 already *is* the presenter-free version, which is exactly what the new video wants. The correlation floor tells you a window is not a pixel match; only a human can say whether that matters | Nothing blocked | Low | **closed** — explained, no work needed |
| OBS-037 | **The change detector was blind to cross-dissolves.** V017's intro is three cards — ekLakshya, KLE Technological University, the title — each fading into the next. Every transition scored **1.5–2.8** on mean absolute difference, against a weak threshold of 10, so the tool reported 0–15.75s as a single window holding three distinct pictures | Fixed. A second metric runs alongside: **percentage of pixels changing by more than 40 levels**. A logo swap on white moves ~1% of pixels enormously — invisible to a mean, obvious to a fraction. Each change now records which metric saw it | Any deck or video using fades rather than cuts | Medium | **closed** |
| OBS-038 | **The source video already contains a hand-authored focus track.** An orange arrow marks what is being discussed, moving between columns and lines. Extracted: **28.6%** of deck-slide time, 20 runs, two x positions (0.04 far-left, 0.54 mid-frame) and y spanning 0.27–0.69 — column and line | Emitted as `focus_ground_truth`. **Use it to check Layer 5's focus map, never to generate one** — 28.6% can confirm a wrong answer but cannot produce a right one. Re-check the colour threshold on V018: it is tuned to orange-on-purple | Layer 5 verification | Medium | open — needs a second video |
| OBS-039 | **The intro and outro already exist and are measured** (closes PROP-002's unknowns). Intro **15.75s**: ekLakshya 1.62s, KLE Technological University 2.88s, title card 4.50s. Outro **15.25s**: THANK YOU FOR WATCHING 4.50s, FOR MORE DETAILS VISIT www.eklakshyaonline.com 2.12s, ekLakshya 1.50s. All cross-dissolves. `©Ravi Subramanian` sits bottom-left throughout — **not `@`**, which contract v5 currently specifies | Reproduce the pattern rather than designing one. Note the closing card is a **call to action**, not just a sign-off. Correct the attribution string in contract v5 to `©Ravi Subramanian`, and check the mark position: the deck footer carries the logo **centred**, not right | TGT-011 duration; contract v5 footer | Medium | open |
| OBS-021 | **Notation tokens may be mis-transcribed, attaching word timings to the wrong words.** Speech recognition renders "Pᵢ" and "Rⱼ" inconsistently ("P I", "pie", "PI"). Forced alignment attaches timings to whatever tokens the transcript contains, so a beat bound to "Rj" can fire on the wrong word. The overall word-error rate will not surface this — the errors are concentrated in exactly the notation-dense segments that matter most | Verification pass on notation-dense segments specifically, separate from the word-error-rate advisory check | Layer 8 accuracy | **High** | open |
| OBS-022 | **Animation durations need a floor and an under-run policy.** When a bound phrase is shorter than the floor (e.g. 0.3 s), drawing a long arrow across it looks frantic. No rule exists for what happens then — compress, run into the following pause, or simplify | Define floor + under-run policy in the style contract. Pairs with OBS-008 | Layer 8 | **High** | open |
| OBS-020 | **The duration row in `competitive-analysis.md` is not a like-for-like comparison** and reads as one. Original 120.1s is the full lecture; competitor 61.0s and ours 83.1s are trimmed demo samples of differing length. This misreading already produced one bad requirement (PROP-001) | Add a note to the row: durations are not comparable; do not infer pacing or content coverage from them | Risk of further false requirements | **High** | open |
| OBS-018 | **Runtime path drift.** The style contract document states `config/style/global_style_contract.json`; the actual file is at `res/config/style/global_style_contract.json` | Correct the document | Anyone following the doc | Low | open |
| OBS-019 | **Nothing read the style contract.** `services/config/` was an empty `__init__.py` | **Resolved by `phase2/config-mgmt`.** `loader.py` reads the contract from `DEFAULT_CONTRACT_PATH`, checks `schema_version`, migrates if needed, and validates through the `StyleContract` model; `resolver.py` flattens the selected theme into one token set. Note: this does **not** close OBS-006 — the v3-document / v1-payload mismatch is two valid strings and passes validation | — | — | **closed — phase2/config-mgmt** |
| OBS-025 | **`docs/engine/architecture.md`'s Phase 2 table marked all eight Config Mgmt items "Completed: NOT STARTED"** while the code was already merged. The docs commit landed before the implementation commit and the table was never updated | **Fixed.** Each of the eight rows verified against the merged code and marked DONE with its supporting module or test; 36-test breakdown added; plus a "not yet wired" note, since no stage calls `load_style_contract()` until Rendering exists | — | — | **closed — fixed** |
| OBS-026 | **The same staleness exists in the Phase 1 table.** Rows **1.5** (Schema Versioning) and **1.7** (Testing/CI) both read NOT STARTED, but `envelope.py` / `migrations.py` exist with their tests (commit `ec37130`), and there are 11 test files with pytest configured and a pre-commit config (commit `04ccf6b`, "78 tests, 96% coverage"). Row 1.6 in the same table already says DONE, so the staleness is per-row | **To be corrected as part of development activity** — deliberately not flipped without verifying what each row actually claims. Deeper fix: make "update the summary table" part of finishing a step, since this is the second table to drift the same way | Nothing; the roadmap misreports project state | Medium | open — deferred to dev |

---

## Summary

| Priority | Open | Closed | Blocking |
|---|---|---|---|
| High | 11 | 2 | Layers 3, 4, 6, 8 |
| Medium | 11 | 4 | — |
| Low | 3 | — | — |

**Baseline: `main` after `phase2/config-mgmt` is merged.** Five items were
closed or narrowed by that branch — OBS-011, OBS-013, OBS-014, OBS-017,
OBS-019.

**Nothing here blocks Layer 2**, whose work is already complete. The first items
that must be resolved are OBS-005 through OBS-008 (before Layer 6 binds entities
and Layer 8 builds beats) and OBS-013 (before Layer 3 produces manifests at
scale).

**Layer 1 status: 3 of 4 closed.** Only OBS-002 remains.

### Closed

| ID | Closed as | Date |
|---|---|---|
| OBS-001 | promoted → TGT-012, TGT-013 | 2026-08-18 |
| OBS-003 | DEC-001 resolved — see note | 2026-08-18 |
| OBS-004 | rejected — see note | 2026-08-18 |
| OBS-011 | resolved by ADR-007 §2, §7 | 2026-08-18 |
| OBS-019 | resolved by `phase2/config-mgmt` | 2026-08-18 |
| OBS-025 | fixed — Phase 2 table verified and updated | 2026-08-18 |

### Layer status

| Layer | Documentation | Output defects |
|---|---|---|
| **1 · Target spec** | ✅ complete — prompt, artifact spec, review | 1 open (OBS-002) |
| **2 · Global theme** | ✅ complete — four-step prompt, artifact spec, review | **7 open** — OBS-005…010, OBS-023 |
| **3 · Asset deconstruction** | ✅ complete — v4 prompt run on the **whole V017 deck**: 5 slides, 45 assets, 50 flags, 3 at error severity. `mpk check manifest` clean | 5 open — OBS-027…029, OBS-033, OBS-034 |
| **4 · Narration timeline** | ✅ complete — v1.2 prompt, `mpk transcript build/export/check/reflag`, review page, 12 review checks. **First real run done on V017** | 1 open — OBS-031. OBS-030 and OBS-032 closed |
| 5 onward | not yet written | — |

**Layer 2's documentation is done; its output is not.** Contract v3 fails six
of the eleven review checks. None of those block Layer 3 or Layer 4 — they
block Layer 6 (entity binding to palette roles) and Layer 8 (pacing and
duration rules).

#### OBS-003 closure note — DEC-001 resolved

**Path A confirmed.** Clean the original recording; the professor's voice is
retained and narration timing is unchanged.

**Consequence: forced alignment is a required component of Transcript
Alignment, not optional.** Registered as an owned item.

| Decision | Detail |
|---|---|
| **Layer 4 emits word-level timings for the entire transcript**, unconditionally | `words[]` with `start_s` / `end_s` is a **Required** field, not Observed. Once the aligner runs, every word is free — selective capture would cost more and put a decision in a facts-only layer |
| **Layer 8 selects the word span** that binds to each visual action | Derives `t_start_s` and `duration_s` from it. Phrase identification is a Layer 8 decision, never a Layer 4 output — an aligner produces words, it cannot know that "from Pᵢ to Rⱼ" is one meaningful unit |
| **Tooling** | `faster-whisper` with `word_timestamps=True`, on the 16 kHz speech-recognition path. Already a project dependency. WhisperX is the fallback if accuracy is insufficient on notation-dense segments |
| **Audio path** | Alignment runs on the 16 kHz mono copy; the 48 kHz stereo master stays separate for delivery. Consistent with RC-003 |
| **Accuracy** | Forced alignment is typically ±20–50 ms, inside the 80 ms sync-drift gate |

**VGR-05 (word/phrase-level pacing) is unblocked.**

**Worked example — why this matters.** Narration: *"Request edge: from Pᵢ to
Rⱼ."* Layer 4 gives every word a start and end. Layer 8 binds beat `b02` (draw
the request edge) to the span "from" → "j", giving start 13.35 s and duration
**1.27 s** — because that is how long he took to say it. The duration is
measured, never chosen. This is the concrete case against the style contract's
fixed `state_motion.duration_s: 1.1` (OBS-008).

#### OBS-004 closure note

#### OBS-004 closure note

PROP-001 is **rejected**, and the row stays in
`findings-and-decisions.md` with this reasoning attached:

> Origin observation (DIFF-006) compared a full lecture against two trimmed
> demo samples — the competitor was not dropping content, they were showing a
> portion of it. The underlying concern is also structurally precluded: with
> narration content and timing fixed (the project invariant), and TGT-011
> requiring the video to span the full transcript, seconds-per-concept is
> inherited from the original lecture and cannot be traded for speed. Nobody
> is shortening the lecture, and the constraints would not permit it.
> Visual-timing concerns remain covered by VGR-05 (word/phrase-level pacing)
> and VGR-07 (content coverage).

**How it was found:** the Layer 1 review checkpoint — asking whether a
requirement still makes sense given what the evidence actually says, rather
than waiting for something downstream to break.
