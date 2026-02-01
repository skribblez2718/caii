"""
End-to-end tests for complete workflow execution.

Tests the full orchestration system from entry point to completion,
including phase transitions, state persistence, and entry point integration.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from orchestration.state.algorithm_state import AlgorithmState, IdealState
from orchestration.state.algorithm_fsm import AlgorithmPhase

# ============================================================================
# Path Constants
# ============================================================================

ORCHESTRATION_ROOT = Path(__file__).parent.parent.parent
ENTRY_POINT = ORCHESTRATION_ROOT / "entry.py"
GATHER_ENTRY = ORCHESTRATION_ROOT / "outer_loop" / "gather" / "entry.py"
IDEAL_STATE_ENTRY = ORCHESTRATION_ROOT / "outer_loop" / "ideal_state" / "entry.py"
OBSERVE_ENTRY = ORCHESTRATION_ROOT / "inner_loop" / "observe" / "entry.py"
VERIFY_ENTRY = ORCHESTRATION_ROOT / "outer_loop" / "verify" / "entry.py"
LEARN_ENTRY = ORCHESTRATION_ROOT / "inner_loop" / "learn" / "entry.py"


def get_subprocess_env(extra_env: dict = None) -> dict:
    """Get environment dict for subprocess with PYTHONPATH set.

    PYTHONPATH is set to the parent of orchestration (e.g., .claude/)
    so that 'from orchestration.state import ...' works correctly.
    """
    env = os.environ.copy()
    # Parent of orchestration so 'orchestration' package is importable
    env["PYTHONPATH"] = str(ORCHESTRATION_ROOT.parent)
    if extra_env:
        env.update(extra_env)
    return env


# ============================================================================
# Test Global Entry Point
# ============================================================================


class TestGlobalEntryPoint:
    """Tests for the global orchestration entry point."""

    @pytest.mark.e2e
    def test_entry_prints_complexity_prompt(self):
        """Entry point should print complexity assessment prompt."""
        result = subprocess.run(
            [sys.executable, str(ENTRY_POINT), "Build a REST API"],
            capture_output=True,
            text=True,
            timeout=10,
            env=get_subprocess_env(),
            check=False,
        )

        assert result.returncode == 0
        # Should print complexity assessment prompt content
        assert (
            "complexity" in result.stdout.lower() or "trivial" in result.stdout.lower()
        )

    @pytest.mark.e2e
    def test_entry_exits_without_args(self):
        """Entry point should exit with error when no args provided."""
        result = subprocess.run(
            [sys.executable, str(ENTRY_POINT)],
            capture_output=True,
            text=True,
            timeout=10,
            env=get_subprocess_env(),
            check=False,
        )

        # argparse uses exit code 2 for argument errors
        assert result.returncode in (1, 2)
        assert "usage:" in result.stderr.lower() or "required" in result.stderr.lower()

    @pytest.mark.e2e
    def test_entry_handles_quoted_query(self):
        """Entry point should handle multi-word quoted query."""
        result = subprocess.run(
            [
                sys.executable,
                str(ENTRY_POINT),
                "Help me build a complex REST API with authentication",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env=get_subprocess_env(),
            check=False,
        )

        assert result.returncode == 0


# ============================================================================
# Test Phase Entry Points
# ============================================================================


class TestPhaseEntryPoints:
    """Tests for individual phase entry points."""

    @pytest.mark.e2e
    def test_gather_entry_exits_without_state(self):
        """GATHER entry should exit when --state not provided."""
        result = subprocess.run(
            [sys.executable, str(GATHER_ENTRY)],
            capture_output=True,
            text=True,
            timeout=10,
            env=get_subprocess_env(),
            check=False,
        )

        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()

    @pytest.mark.e2e
    def test_gather_entry_exits_for_invalid_session(self):
        """GATHER entry should exit for non-existent session."""
        result = subprocess.run(
            [sys.executable, str(GATHER_ENTRY), "--state", "nonexistent12"],
            capture_output=True,
            text=True,
            timeout=10,
            env=get_subprocess_env(),
            check=False,
        )

        assert result.returncode == 1
        assert "not found" in result.stderr.lower()

    @pytest.mark.e2e
    def test_gather_entry_with_valid_session(self):
        """GATHER entry should work with valid session.

        Note: This test uses the real sessions directory since subprocess
        cannot share the monkeypatched temp directory.
        """
        # Create state (uses real sessions directory)
        state = AlgorithmState(user_query="E2E test query")
        state.save()

        try:
            result = subprocess.run(
                [sys.executable, str(GATHER_ENTRY), "--state", state.session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
                check=False,
            )

            assert result.returncode == 0
            # Should print phase content
            assert len(result.stdout) > 0
        finally:
            # Cleanup: remove the state file
            state.state_file_path.unlink(missing_ok=True)

    @pytest.mark.e2e
    def test_ideal_state_entry_requires_gather_complete(self):
        """IDEAL_STATE entry should fail if GATHER not completed.

        Note: This test uses the real sessions directory since subprocess
        cannot share the monkeypatched temp directory.
        """
        # Create state but don't complete GATHER (uses real sessions directory)
        state = AlgorithmState(user_query="E2E test")
        state.save()

        try:
            result = subprocess.run(
                [sys.executable, str(IDEAL_STATE_ENTRY), "--state", state.session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
                check=False,
            )

            # Should fail because FSM can't transition INITIALIZED -> IDEAL_STATE
            assert result.returncode == 1
        finally:
            # Cleanup: remove the state file
            state.state_file_path.unlink(missing_ok=True)


# ============================================================================
# Test Complete Workflow Simulation
# ============================================================================


class TestCompleteWorkflowSimulation:
    """Tests for simulating complete workflow through state manipulation."""

    @pytest.mark.e2e
    def test_complete_workflow_initialized_to_completed(self, mock_sessions_dir):
        """Simulate complete workflow from INITIALIZED to COMPLETED."""
        # Create initial state
        state = AlgorithmState(user_query="Build a comprehensive REST API")
        state.save()
        session_id = state.session_id

        # Simulate GATHER phase
        state = AlgorithmState.load(session_id)
        assert state.start_phase(AlgorithmPhase.GATHER)
        state.set_current_state(
            domain="CODING",
            state_data={
                "known_knowns": ["REST API", "Python"],
                "known_unknowns": ["Database"],
            },
        )
        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "complete"})
        state.save()

        # Simulate INTERVIEW phase
        state = AlgorithmState.load(session_id)
        assert state.start_phase(AlgorithmPhase.INTERVIEW)
        ideal = IdealState(
            task_id=session_id,
            task_type="feature",
            objective="Build a REST API",
            euphoric_surprise="Fast and secure",
            completeness_score=0.95,
        )
        state.set_ideal_state(ideal)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"ideal_state": "captured"})
        state.save()

        # Simulate INNER_LOOP phase
        state = AlgorithmState.load(session_id)
        assert state.start_phase(AlgorithmPhase.INNER_LOOP)
        state.record_phase_output(
            AlgorithmPhase.INNER_LOOP,
            {
                "observe": "complete",
                "think": "complete",
                "plan": "complete",
                "build": "complete",
                "execute": "complete",
            },
        )
        state.save()

        # Simulate VERIFY phase
        state = AlgorithmState.load(session_id)
        assert state.start_phase(AlgorithmPhase.VERIFY)
        state.record_phase_output(AlgorithmPhase.VERIFY, {"verification": "passed"})
        state.save()

        # Simulate LEARN phase
        state = AlgorithmState.load(session_id)
        assert state.start_phase(AlgorithmPhase.LEARN)
        state.record_phase_output(
            AlgorithmPhase.LEARN, {"learnings": ["API patterns", "TDD worked"]}
        )
        state.save()

        # Complete the workflow
        state = AlgorithmState.load(session_id)
        state.complete()
        state.save()

        # Verify final state
        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.COMPLETED
        assert final.status == "completed"
        assert len(final.phase_outputs) >= 5  # All phases

    @pytest.mark.e2e
    def test_workflow_with_loop_back(self, mock_sessions_dir):
        """Simulate workflow with loop-back from VERIFY."""
        state = AlgorithmState(user_query="Build API with iteration")
        state.save()
        session_id = state.session_id

        # First pass through phases to VERIFY
        state = AlgorithmState.load(session_id)
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {"pass1": "done"})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"pass1": "done"})
        state.start_phase(AlgorithmPhase.INNER_LOOP)
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"pass1": "done"})
        state.start_phase(AlgorithmPhase.VERIFY)
        state.save()

        # VERIFY fails, loop back
        state = AlgorithmState.load(session_id)
        assert state.loop_back_to_inner_loop()
        state.save()

        # Second pass from INNER_LOOP
        state = AlgorithmState.load(session_id)
        assert state.current_phase == AlgorithmPhase.INNER_LOOP
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"pass2": "done"})
        state.start_phase(AlgorithmPhase.VERIFY)
        state.record_phase_output(AlgorithmPhase.VERIFY, {"verification": "passed"})
        state.save()

        # Complete
        state = AlgorithmState.load(session_id)
        state.start_phase(AlgorithmPhase.LEARN)
        state.record_phase_output(
            AlgorithmPhase.LEARN, {"learnings": "iteration worked"}
        )
        state.complete()
        state.save()

        # Verify
        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.COMPLETED
        assert final.outer_loop_iteration == 1

    @pytest.mark.e2e
    @pytest.mark.skip(reason="Halt/resume workflow not implemented")
    def test_workflow_with_halt_resume(self, mock_sessions_dir):
        """Simulate workflow with halt and resume."""
        # This test is skipped because halt_for_clarification() and
        # resume_from_halt() are not implemented in the current API
        pass


# ============================================================================
# Test Complexity Routing (5 METR Categories)
# ============================================================================


class TestComplexityRouting:
    """Tests for complexity extraction and routing logic with 5 METR categories."""

    @pytest.mark.e2e
    def test_extract_complexity_trivial(self):
        """Should extract 'trivial' from various response formats."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "trivial",
            "TRIVIAL",
            "This is a trivial task",
            "Classification: trivial",
        ]

        for response in test_cases:
            assert extract_complexity(response) == "trivial", f"Failed for: {response}"

    @pytest.mark.e2e
    def test_extract_complexity_simple(self):
        """Should extract 'simple' from various response formats."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "simple",
            "SIMPLE",
            "This is a simple task",
            "Classification: simple",
        ]

        for response in test_cases:
            assert extract_complexity(response) == "simple", f"Failed for: {response}"

    @pytest.mark.e2e
    def test_extract_complexity_moderate(self):
        """Should extract 'moderate' from various response formats."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "moderate",
            "MODERATE",
            "This is a moderate task",
            "Classification: moderate",
        ]

        for response in test_cases:
            assert extract_complexity(response) == "moderate", f"Failed for: {response}"

    @pytest.mark.e2e
    def test_extract_complexity_complex(self):
        """Should extract 'complex' from various response formats."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "complex",
            "COMPLEX",
            "This is a complex task",
            "Classification: complex",
        ]

        for response in test_cases:
            assert extract_complexity(response) == "complex", f"Failed for: {response}"

    @pytest.mark.e2e
    def test_extract_complexity_very_complex(self):
        """Should extract 'very_complex' from various response formats."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "very complex",
            "VERY COMPLEX",
            "very-complex",
            "very_complex",
            "This is a very complex task",
            "Classification: very complex",
        ]

        for response in test_cases:
            assert (
                extract_complexity(response) == "very_complex"
            ), f"Failed for: {response}"

    @pytest.mark.e2e
    def test_extract_complexity_unknown(self):
        """Should return 'unknown' for unrecognized responses."""
        from orchestration.entry import extract_complexity

        test_cases = [
            "medium difficulty",
            "hard",
            "",
        ]

        for response in test_cases:
            assert extract_complexity(response) == "unknown", f"Failed for: {response}"

    @pytest.mark.e2e
    def test_simple_route_to_gather(self, mock_sessions_dir, capsys):
        """Simple route should create state and route to GATHER."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("simple", "Simple task")

        captured = capsys.readouterr()

        assert "Last Algorithm" in captured.out
        assert "SIMPLE" in captured.out
        assert "gather" in captured.out.lower()
        assert "--state" in captured.out

    @pytest.mark.e2e
    def test_moderate_route_to_gather(self, mock_sessions_dir, capsys):
        """Moderate route should create state and route to GATHER."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("moderate", "Moderate task")

        captured = capsys.readouterr()

        assert "Last Algorithm" in captured.out
        assert "MODERATE" in captured.out
        assert "gather" in captured.out.lower()

    @pytest.mark.e2e
    def test_complex_route_to_decompose(self, mock_sessions_dir, capsys):
        """Complex route should create state and route to DECOMPOSE."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("complex", "Complex task")

        captured = capsys.readouterr()

        assert "DECOMPOSE" in captured.out
        assert "COMPLEX" in captured.out
        assert "decompose" in captured.out.lower()

    @pytest.mark.e2e
    def test_very_complex_route_to_decompose(self, mock_sessions_dir, capsys):
        """Very complex route should create state and route to DECOMPOSE."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("very complex", "Very complex task")

        captured = capsys.readouterr()

        assert "DECOMPOSE" in captured.out
        assert "VERY COMPLEX" in captured.out
        assert "decompose" in captured.out.lower()

    @pytest.mark.e2e
    def test_state_has_correct_complexity(self, mock_sessions_dir):
        """All categories should store correct complexity value in state."""
        import json

        from orchestration.entry import route_based_on_complexity

        test_cases = [
            ("simple", "simple"),
            ("moderate", "moderate"),
            ("complex", "complex"),
            ("very complex", "very_complex"),
        ]

        for i, (response, expected) in enumerate(test_cases):
            # Clear any previous state files for this test
            for f in mock_sessions_dir.glob("algorithm-*.json"):
                f.unlink()

            route_based_on_complexity(response, f"Test task {i}")

            session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
            assert len(session_files) == 1, f"Expected 1 state file for {response}"

            with open(session_files[0], "r", encoding="utf-8") as f:
                state_data = json.load(f)

            assert state_data["complexity"] == expected, f"Failed for: {response}"

    @pytest.mark.e2e
    def test_trivial_route_no_state_created(self, mock_sessions_dir, capsys):
        """Trivial route should not create algorithm state."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("trivial", "What time is it?")

        captured = capsys.readouterr()

        # Should mention direct execution
        assert "Direct Execution" in captured.out or "trivial" in captured.out.lower()
        # Should NOT include session or state
        assert "--state" not in captured.out

        # No state file should be created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 0


# ============================================================================
# Test Entry Point Subprocess Chain
# ============================================================================


class TestEntryPointSubprocessChain:
    """Tests for entry point subprocess execution chain.

    Note: These tests use the real sessions directory since subprocess
    cannot share monkeypatched temp directories with the parent process.
    """

    @pytest.mark.e2e
    def test_gather_updates_state_file(self):
        """GATHER entry should update state file."""
        # Create initial state (uses real sessions directory)
        state = AlgorithmState(user_query="Subprocess chain test")
        state.save()
        session_id = state.session_id

        try:
            # Run GATHER entry
            result = subprocess.run(
                [sys.executable, str(GATHER_ENTRY), "--state", session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
                check=False,
            )

            assert result.returncode == 0

            # Verify state was updated
            loaded = AlgorithmState.load(session_id)
            assert loaded.current_phase == AlgorithmPhase.GATHER
            assert "GATHER" in loaded.phase_timestamps
        finally:
            # Cleanup
            state = AlgorithmState.load(session_id)
            if state:
                state.state_file_path.unlink(missing_ok=True)

    @pytest.mark.e2e
    def test_phase_sequence_via_subprocess(self):
        """Test sequential phase execution via subprocess."""
        # Create initial state (uses real sessions directory)
        state = AlgorithmState(user_query="Multi-phase subprocess test")
        state.save()
        session_id = state.session_id

        try:
            # Execute GATHER via subprocess
            result = subprocess.run(
                [sys.executable, str(GATHER_ENTRY), "--state", session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
                check=False,
            )
            assert result.returncode == 0

            # Manually complete GATHER for next phase
            state = AlgorithmState.load(session_id)
            state.record_phase_output(AlgorithmPhase.GATHER, {"gather": "done"})
            state.save()

            # Execute IDEAL_STATE via subprocess
            result = subprocess.run(
                [sys.executable, str(IDEAL_STATE_ENTRY), "--state", session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
                check=False,
            )
            assert result.returncode == 0

            # Verify progression
            loaded = AlgorithmState.load(session_id)
            assert loaded.current_phase == AlgorithmPhase.INTERVIEW
        finally:
            # Cleanup
            state = AlgorithmState.load(session_id)
            if state:
                state.state_file_path.unlink(missing_ok=True)
