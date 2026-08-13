"""
Unit tests for src/pipeline/orchestrator.py — Phase 1, Task 7.

Uses a FakeStageRunner (subclassing ContainerStageRunner, overriding
run_stage entirely) so these tests exercise the orchestrator's real
logic — dependency resolution, checkpoint/resume, retry/backoff,
auto/manual review branching — without needing a real LXD environment.
"""

from pathlib import Path

import pytest

from pipeline.core import registry
from pipeline.core.manifest import Artifact, StageManifest
from pipeline.orchestrator import ContainerStageRunner, Orchestrator, StageExecutionError


def _register_fork_join_pipeline():
    """The same 5-stage fork/join shape as the real pipeline design:
    sequence_mapping needs BOTH visual_deconstruction and
    transcript_alignment; video_compose is a straight chain after that."""
    registry.register_stage("visual_deconstruction", "pipeline-structure")
    registry.register_stage("transcript_alignment", "pipeline-speech")
    registry.register_stage(
        "sequence_mapping", "pipeline-structure",
        depends_on=["visual_deconstruction", "transcript_alignment"],
        is_gate=True,
    )
    registry.register_stage("html_build", "pipeline-render", depends_on=["sequence_mapping"])
    registry.register_stage(
        "video_compose", "pipeline-render", depends_on=["html_build"], is_gate=True
    )


class FakeStageRunner(ContainerStageRunner):
    """
    Records every call in self.call_log. Produces a deterministic
    checksum per invocation (sha256:<stage>_run<N>) so a genuine re-run
    naturally produces a different checksum, same as real rendering would.
    Stages listed in self.fail_until_attempt raise StageExecutionError
    until that many attempts have been made.
    """

    def __init__(self, tmp_path):
        super().__init__(host_workdir_root=tmp_path)
        self.call_log: list[str] = []
        self.run_counts: dict[str, int] = {}
        self.fail_until_attempt: dict[str, int] = {}

    def run_stage(self, job_id, stage_name, container_name, input_manifest):
        self.call_log.append(stage_name)
        self.run_counts[stage_name] = self.run_counts.get(stage_name, 0) + 1
        n = self.run_counts[stage_name]

        if n <= self.fail_until_attempt.get(stage_name, 0):
            raise StageExecutionError(f"simulated failure #{n} for {stage_name}")

        checksum = f"sha256:{stage_name}_run{n}"
        return StageManifest(
            stage_name=stage_name,
            artifacts=[
                Artifact(
                    artifact_type=f"{stage_name}_output",
                    file_path=f"res/workdir/{job_id}/{stage_name}/out.json",
                    checksum=checksum,
                )
            ],
        )


@pytest.fixture
def orchestrator(repo, tmp_path):
    _register_fork_join_pipeline()
    runner = FakeStageRunner(tmp_path)
    orch = Orchestrator(repo, runner, max_attempts=3, sleep_fn=lambda s: None)
    return orch, runner, repo


def test_fork_join_waits_for_both_dependencies(orchestrator):
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")

    result = orch.run_job(job_id)

    assert result.outcome == "waiting_review"
    assert result.stage_name == "sequence_mapping"
    assert runner.call_log == ["visual_deconstruction", "transcript_alignment", "sequence_mapping"]


def test_manual_mode_does_not_rerun_while_pending(orchestrator):
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")
    orch.run_job(job_id)

    runner.call_log.clear()
    result = orch.run_job(job_id)

    assert result.outcome == "waiting_review"
    assert runner.call_log == [], "must not re-run a stage that's already completed and pending review"


def test_manual_mode_full_flow_with_approvals(orchestrator):
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")

    orch.run_job(job_id)  # pauses at sequence_mapping
    orch.approve_current_gate(job_id)
    runner.call_log.clear()
    result2 = orch.run_job(job_id)
    assert result2.outcome == "waiting_review"
    assert result2.stage_name == "video_compose"
    assert runner.call_log == ["html_build", "video_compose"]

    orch.approve_current_gate(job_id)
    runner.call_log.clear()
    result3 = orch.run_job(job_id)
    assert result3.outcome == "completed"
    assert runner.call_log == []
    assert repo.get_job(job_id).status == "completed"


def test_auto_mode_runs_straight_through(orchestrator):
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")

    result = orch.run_job(job_id)

    assert result.outcome == "completed"
    assert runner.call_log == [
        "visual_deconstruction", "transcript_alignment",
        "sequence_mapping", "html_build", "video_compose",
    ]
    seq_stage = repo.get_stage(job_id, "sequence_mapping")
    assert seq_stage.review_status == "auto_approved"


def test_retry_succeeds_within_max_attempts(orchestrator):
    orch, runner, repo = orchestrator
    runner.fail_until_attempt["transcript_alignment"] = 2  # fails twice, succeeds 3rd
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")

    sleeps = []
    orch._sleep = lambda s: sleeps.append(s)

    result = orch.run_job(job_id)

    assert result.outcome == "completed"
    assert runner.call_log.count("transcript_alignment") == 3
    assert sleeps == [2, 8]
    stage = repo.get_stage(job_id, "transcript_alignment")
    assert stage.attempt_count == 3
    assert stage.status == "completed"


def test_retry_exhaustion_fails_job(orchestrator):
    orch, runner, repo = orchestrator
    runner.fail_until_attempt["html_build"] = 999  # never succeeds
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")

    result = orch.run_job(job_id)

    assert result.outcome == "failed"
    assert result.stage_name == "html_build"
    assert runner.call_log.count("html_build") == 3  # exactly max_attempts, no more
    assert repo.get_job(job_id).status == "failed"


def test_resumability_only_reruns_downstream_of_a_changed_artifact(orchestrator):
    """
    The scenario the whole checksum-based design exists for: a human edits
    an intermediate artifact (e.g. plan.json) after the job completed.
    Only stages that actually depend on that artifact should re-run.
    """
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "auto")
    orch.run_job(job_id)  # full run, completes

    before = repo.get_stage(job_id, "html_build").checkpoint_data["input_checksums"]

    # Simulate a human editing sequence_mapping's output on disk — this is
    # exactly what repository.upsert_artifact does when a file's checksum
    # is recomputed after an edit (see Task 3).
    repo.upsert_artifact(
        job_id, "sequence_mapping", "sequence_mapping_output",
        "res/workdir/j/sequence_mapping/out.json",
        "sha256:EDITED_BY_HUMAN",
    )
    repo.set_job_status(job_id, "in_progress")  # what `pipeline resume` does

    runner.call_log.clear()
    result = orch.run_job(job_id)

    assert result.outcome == "completed"
    assert "visual_deconstruction" not in runner.call_log
    assert "transcript_alignment" not in runner.call_log
    assert "sequence_mapping" not in runner.call_log, "its own inputs didn't change"
    assert "html_build" in runner.call_log, "its input (sequence_mapping's output) changed"
    assert "video_compose" in runner.call_log, "depends on html_build's now-changed output"

    after = repo.get_stage(job_id, "html_build").checkpoint_data["input_checksums"]
    assert after != before


def test_approve_current_gate_raises_when_nothing_pending(orchestrator):
    orch, runner, repo = orchestrator
    job_id = repo.create_job("a.pptx", "a.mp4", "manual")
    with pytest.raises(ValueError):
        orch.approve_current_gate(job_id)  # nothing has run yet, nothing pending


class TestContainerStageRunnerDirect:
    """
    Tests ContainerStageRunner itself (not the FakeStageRunner subclass
    used elsewhere) — path translation and error handling, using an
    injected exec_fn so no real `lxc` binary is needed.
    """

    def test_to_container_path_translation(self, tmp_path):
        runner = ContainerStageRunner(host_workdir_root=tmp_path, exec_fn=lambda cmd: None)
        host_path = tmp_path / "job123" / "visual_deconstruction_input.json"
        assert runner._to_container_path(host_path) == "/workdir/job123/visual_deconstruction_input.json"

    def test_run_stage_invokes_exec_fn_with_correct_command(self, tmp_path):
        captured_cmds = []

        def fake_exec(cmd):
            captured_cmds.append(cmd)
            # Simulate the container writing its output file, since the
            # real `lxc exec` call would have done this as a side effect.
            output_path = Path(cmd[cmd.index("--output") + 1].replace("/workdir", str(tmp_path)))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                StageManifest(stage_name="x", artifacts=[]).model_dump_json()
            )

        runner = ContainerStageRunner(host_workdir_root=tmp_path, exec_fn=fake_exec)
        input_manifest = StageManifest(stage_name="x", artifacts=[])
        result = runner.run_stage("job1", "x", "pipeline-structure", input_manifest)

        assert result.stage_name == "x"
        cmd = captured_cmds[0]
        assert cmd[:3] == ["lxc", "exec", "pipeline-structure"]
        assert "run-stage" in cmd
        assert "x" in cmd

    def test_run_stage_raises_if_output_file_never_appears(self, tmp_path):
        # exec_fn does nothing — simulates a container that "succeeds"
        # (exit 0) but never actually wrote its output file.
        runner = ContainerStageRunner(host_workdir_root=tmp_path, exec_fn=lambda cmd: None)
        input_manifest = StageManifest(stage_name="x", artifacts=[])
        with pytest.raises(StageExecutionError):
            runner.run_stage("job1", "x", "pipeline-structure", input_manifest)

    def test_real_exec_raises_on_nonzero_exit(self, tmp_path):
        runner = ContainerStageRunner(host_workdir_root=tmp_path)  # default _real_exec
        with pytest.raises(StageExecutionError):
            runner._real_exec(["false"])  # `false` always exits 1

    def test_real_exec_succeeds_on_zero_exit(self, tmp_path):
        runner = ContainerStageRunner(host_workdir_root=tmp_path)
        runner._real_exec(["true"])  # `true` always exits 0 — must not raise
