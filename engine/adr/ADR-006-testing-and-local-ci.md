# ADR-006 · Testing and local CI infrastructure

Status:   accepted
Date:     2026-08-12
Context:  Phase 1 — Pipeline Foundations (originally section 1.7 of the
          foundation document)

> Extracted verbatim from `docs/engine/architecture.html` during the docs
> restructure. Content unchanged; only the container moved. Append-only from
> here — supersede with a new ADR rather than editing this one.

## Concrete Design

**Test runner: `pytest` with `pytest-cov`. Golden-file regression via small, checked-in fixture media (<1MB each) and deterministic-where-possible comparisons.**

- **Unit tests** (`tests/unit/`): pure logic, no media I/O — schema validation, checkpoint skip/resume logic, migration functions, threshold comparisons. Fast, run on every save.
- **Integration tests** (`tests/integration/`): run a real stage against a tiny fixture and assert on structural properties (artifact exists, checksum stable, duration within tolerance) — not byte-for-byte comparison, since TTS/render output is non-deterministic.
- **Golden-file regression** for deterministic stages only (PPTX parsing, alignment timing math): exact-match golden files. For non-deterministic stages (TTS, render), replaced by property-based validation (duration bounds, format correctness, threshold gates from 1.6).
- **Local CI**: no external CI service needed for a solo 5-day local build — a `Makefile`/`justfile` target run manually or via pre-commit is sufficient.

## Trade-offs & Edge Cases

- **Media fixtures bloating the repo**: cap fixtures at <1MB each, document regeneration steps in `tests/fixtures/README.md`.
- **Flaky non-deterministic assertions**: never assert exact TTS output hashes; assert bounded properties.
- **Over-investing in CI infra on Day 1** is itself a risk — a `Makefile` + `pytest` is the entire CI system for Phase 1, full stop.

## Claude Code Implementation Spec

*Spec file: `testing-ci.txt`*
```
Task: Set up pytest-based test infrastructure with golden-file and property tests.

1. Create pyproject.toml [tool.pytest.ini_options]:
   testpaths = ["tests"]
   markers = ["unit", "integration", "slow"]

2. Create tests/fixtures/:
   - sample_3slide.pptx (small, checked in)
   - sample_5sec.mp4 (small, checked in)
   - README.md documenting how each was generated

3. Create tests/golden/ for deterministic-stage golden files:
   - expected_ingest_output.json (structured PPTX parse result)
   - expected_alignment_timing.json

4. Create tests/unit/test_checkpointing.py:
   - test_should_skip_stage_when_checksum_matches
   - test_should_rerun_stage_when_input_changed
   - test_retry_exhaustion_marks_job_failed

5. Create tests/unit/test_schema_versioning.py:
   - test_missing_schema_version_raises
   - test_migration_chain_applies_in_order

6. Create tests/integration/test_ingest_stage.py:
   - Runs ingest stage against sample_3slide.pptx, diffs structured output
     against tests/golden/expected_ingest_output.json (exact match — 
     deterministic stage)

7. Create tests/integration/test_render_stage.py:
   - Runs render stage against fixtures, asserts PROPERTY-based checks only:
     duration within tolerance, fps >= threshold, ffprobe exit 0
     (NOT exact byte comparison — non-deterministic stage)

8. Create justfile (or Makefile) at repo root:
   test:        pytest tests/unit -v
   test-full:   pytest tests -v --cov=src/pipeline
   check:       ruff check . && mypy src/pipeline && just test

9. Add .pre-commit-config.yaml (optional but recommended) running ruff +
   mypy + `just test` on commit.
```
