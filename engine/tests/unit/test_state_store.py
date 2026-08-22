"""
Unit tests for src/pipeline/state/ (repository.py, db.py) — Phase 1, Task 3.

Converted from the ad-hoc verification run during Task 3's build into a
permanent, re-runnable suite.
"""

import time

import pytest


def test_create_job_defaults(repo):
    job_id = repo.create_job("res/inputs/j/deck.pptx", "res/inputs/j/lecture.mp4", "manual")
    job = repo.get_job(job_id)
    assert job.status == "in_progress"
    assert job.review_mode == "manual"
    assert job.schema_version == "1.0.0"


def test_create_job_rejects_bad_review_mode(repo):
    with pytest.raises(ValueError):
        repo.create_job("a.pptx", "a.mp4", "sometimes")


def test_job_id_format(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    assert job_id.startswith("job_")
    assert len(job_id.split("_")) == 3  # job_<date>_<hex>


def test_stage_lifecycle_start_complete(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")
    repo.start_stage(job_id, "visual_deconstruction", container_name="pipeline-structure")
    stage = repo.get_stage(job_id, "visual_deconstruction")
    assert stage.status == "running"
    assert stage.attempt_count == 1
    assert stage.container_name == "pipeline-structure"

    repo.complete_stage(job_id, "visual_deconstruction", {"output_checksum": "sha256:abc"})
    stage = repo.get_stage(job_id, "visual_deconstruction")
    assert stage.status == "completed"
    assert stage.checkpoint_data == {"output_checksum": "sha256:abc"}
    assert stage.review_status == "not_applicable"  # default when not specified


def test_stage_retry_increments_attempt_count(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.start_stage(job_id, "audio_preprocessing")
    repo.fail_stage(job_id, "audio_preprocessing", "simulated crash")
    stage = repo.get_stage(job_id, "audio_preprocessing")
    assert stage.status == "failed"
    assert stage.attempt_count == 1

    repo.start_stage(job_id, "audio_preprocessing")  # retry
    stage = repo.get_stage(job_id, "audio_preprocessing")
    assert stage.status == "running"
    assert stage.attempt_count == 2


def test_review_status_gate_flow(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")
    repo.start_stage(job_id, "sequence_mapping")
    repo.complete_stage(job_id, "sequence_mapping", {}, review_status="pending")
    stage = repo.get_stage(job_id, "sequence_mapping")
    assert stage.review_status == "pending"

    repo.set_review_status(job_id, "sequence_mapping", "approved")
    stage = repo.get_stage(job_id, "sequence_mapping")
    assert stage.review_status == "approved"


def test_review_status_rejects_invalid_value(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")
    repo.start_stage(job_id, "x")
    with pytest.raises(ValueError):
        repo.complete_stage(job_id, "x", {}, review_status="maybe")


def test_artifact_upsert_creates_then_updates_on_checksum_change(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.upsert_artifact(job_id, "sequence_mapping", "plan_json", "res/workdir/j/plan.json", "sha256:v1")
    art = repo.get_artifact(job_id, "sequence_mapping", "plan_json")
    assert art.checksum == "sha256:v1"
    first_updated_at = art.updated_at

    time.sleep(1.1)  # ensure the timestamp actually changes (second-resolution)
    repo.upsert_artifact(job_id, "sequence_mapping", "plan_json", "res/workdir/j/plan.json", "sha256:v2_EDITED")
    art2 = repo.get_artifact(job_id, "sequence_mapping", "plan_json")
    assert art2.checksum == "sha256:v2_EDITED"
    assert art2.updated_at != first_updated_at, "updated_at must bump when checksum changes"


def test_artifact_upsert_is_noop_when_checksum_unchanged(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.upsert_artifact(job_id, "s", "t", "path", "sha256:same")
    before = repo.get_artifact(job_id, "s", "t")
    repo.upsert_artifact(job_id, "s", "t", "path", "sha256:same")  # identical checksum
    after = repo.get_artifact(job_id, "s", "t")
    assert before.updated_at == after.updated_at


def test_get_resumable_jobs_excludes_completed(repo):
    j1 = repo.create_job("a.pptx", "a.mp4", "auto")
    j2 = repo.create_job("b.pptx", "b.mp4", "auto")
    repo.set_job_status(j1, "completed")

    resumable_ids = {j.id for j in repo.get_resumable_jobs()}
    assert j1 not in resumable_ids
    assert j2 in resumable_ids


def test_get_last_checkpoint_returns_none_if_not_completed(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.start_stage(job_id, "x")  # running, not completed
    assert repo.get_last_checkpoint(job_id, "x") is None


def test_get_last_checkpoint_returns_data_when_completed(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.start_stage(job_id, "x")
    repo.complete_stage(job_id, "x", {"sync_drift_ms": 42})
    assert repo.get_last_checkpoint(job_id, "x") == {"sync_drift_ms": 42}


def test_list_artifacts_filters_by_stage(repo):
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    repo.upsert_artifact(job_id, "stage_a", "type1", "path1", "c1")
    repo.upsert_artifact(job_id, "stage_b", "type2", "path2", "c2")

    all_artifacts = repo.list_artifacts(job_id)
    assert len(all_artifacts) == 2

    stage_a_only = repo.list_artifacts(job_id, stage_name="stage_a")
    assert len(stage_a_only) == 1
    assert stage_a_only[0].artifact_type == "type1"


def test_foreign_key_enforced_for_orphan_stage(repo):
    with pytest.raises(Exception):  # sqlite3.IntegrityError
        repo.start_stage("nonexistent_job_id", "some_stage")


def test_migration_is_idempotent(tmp_path, monkeypatch):
    """Reconnecting to an already-migrated DB must not error or re-apply."""
    from pipeline.state import db

    db_path = tmp_path / "idempotent.db"
    conn1 = db.connect(db_path)
    conn1.close()

    conn2 = db.connect(db_path)  # second connect, migrations already applied
    applied = db.apply_migrations(conn2)
    assert applied == []
    conn2.close()
