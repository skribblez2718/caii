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
        )

        assert result.returncode == 1
        assert "not found" in result.stderr.lower()

    @pytest.mark.e2e
    def test_gather_entry_with_valid_session(self):
        """GATHER entry should work with valid session.

        Note: This test uses the real sessions directory since subprocess
        cannot share the monkeypatched temp directory.
        """
        from orchestration.state import AlgorithmState

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
        from orchestration.state import AlgorithmState

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
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        # Create initial state
        state = AlgorithmState(user_query="Build a comprehensive REST API")
        state.save()
        session_id = state.session_id

        # Simulate GATHER phase (Step 0)
        state = AlgorithmState.load(session_id)
        assert state.start_phase(0)
        state.update_johari_schema(
            {
                "known_knowns": ["REST API", "Python"],
                "known_unknowns": ["Database"],
            }
        )
        state.complete_phase(0, {"johari": "complete"})
        state.save()

        # Simulate IDEAL_STATE phase (Step 0.5)
        state = AlgorithmState.load(session_id)
        assert state.start_phase(0.5)
        state.update_ideal_state(
            {
                "success_criteria": ["API responds correctly", "Tests pass"],
                "anti_criteria": ["No security vulnerabilities"],
            },
            completeness_score=0.95,
        )
        state.complete_phase(0.5, {"ideal_state": "captured"})
        state.save()

        # Simulate inner loop phases
        for step, name in [
            (1, "observe"),
            (2, "think"),
            (3, "plan"),
            (4, "build"),
            (5, "execute"),
        ]:
            state = AlgorithmState.load(session_id)
            assert state.start_phase(step)
            state.complete_phase(step, {name: "complete"})
            state.save()

        # Simulate VERIFY phase (Step 8)
        state = AlgorithmState.load(session_id)
        assert state.start_phase(8)
        state.add_verification_result({"all_tests": "pass"}, passed=True)
        state.complete_phase(8, {"verification": "passed"})
        state.save()

        # Simulate LEARN phase (Step 8.5)
        state = AlgorithmState.load(session_id)
        assert state.start_phase(8.5)
        state.complete_phase(8.5, {"learnings": ["API patterns", "TDD worked"]})
        state.save()

        # Complete the workflow
        state = AlgorithmState.load(session_id)
        assert state.mark_completed()
        state.save()

        # Verify final state
        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.COMPLETED
        assert final.status == "completed"
        assert len(final.phase_outputs) >= 9  # All phases

    @pytest.mark.e2e
    def test_workflow_with_loop_back(self, mock_sessions_dir):
        """Simulate workflow with loop-back from VERIFY."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API with iteration")
        state.save()
        session_id = state.session_id

        # First pass through all phases to VERIFY
        phases = [0, 0.5, 1, 2, 3, 4, 5]
        for step in phases:
            state = AlgorithmState.load(session_id)
            state.start_phase(step)
            state.complete_phase(step, {f"pass1_step{step}": "done"})
            state.save()

        # VERIFY fails
        state = AlgorithmState.load(session_id)
        state.start_phase(8)
        state.add_verification_result({"tests": "failed"}, passed=False)
        state.save()

        # Loop back to BUILD
        state = AlgorithmState.load(session_id)
        assert state.fsm.loop_back(AlgorithmPhase.BUILD)
        state.save()

        # Second pass from BUILD
        state = AlgorithmState.load(session_id)
        assert state.current_phase == AlgorithmPhase.BUILD
        state.complete_phase(4, {"pass2_build": "done"})
        state.start_phase(5)
        state.complete_phase(5, {"pass2_execute": "done"})
        state.save()

        # VERIFY passes
        state = AlgorithmState.load(session_id)
        state.start_phase(8)
        state.add_verification_result({"tests": "passed"}, passed=True)
        state.complete_phase(8, {"verification": "passed"})
        state.save()

        # Complete
        state = AlgorithmState.load(session_id)
        state.start_phase(8.5)
        state.complete_phase(8.5, {"learnings": "iteration worked"})
        state.save()

        state = AlgorithmState.load(session_id)
        assert state.mark_completed()
        state.save()

        # Verify
        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.COMPLETED
        assert final.fsm.iteration_count == 1
        assert len(final.verification_results) == 2

    @pytest.mark.e2e
    def test_workflow_with_halt_resume(self, mock_sessions_dir):
        """Simulate workflow with halt and resume."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API with clarification needed")
        state.save()
        session_id = state.session_id

        # Progress to GATHER
        state = AlgorithmState.load(session_id)
        state.start_phase(0)
        state.save()

        # Halt for clarification
        state = AlgorithmState.load(session_id)
        state.halt_for_clarification(
            reason="Ambiguous requirements",
            questions=["Which database?", "Auth method?"],
        )
        state.save()

        # Verify halt persisted
        halted = AlgorithmState.load(session_id)
        assert halted.current_phase == AlgorithmPhase.HALTED
        assert halted.status == "halted"

        # Resume
        state = AlgorithmState.load(session_id)
        state.resume_from_halt(
            target_step=0,
            clarification_response={"database": "PostgreSQL", "auth": "JWT"},
        )
        state.save()

        # Verify resume
        resumed = AlgorithmState.load(session_id)
        assert resumed.current_phase == AlgorithmPhase.GATHER
        assert resumed.status == "in_progress"
        assert resumed.metadata["last_clarification"]["database"] == "PostgreSQL"

        # Continue to completion
        state = AlgorithmState.load(session_id)
        state.complete_phase(0, {"johari": "done"})

        for step in [0.5, 1, 2, 3, 4, 5, 8, 8.5]:
            state.start_phase(step)
            state.complete_phase(step, {f"step{step}": "done"})

        state.mark_completed()
        state.save()

        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.COMPLETED


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
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

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
            )

            assert result.returncode == 0

            # Verify state was updated
            loaded = AlgorithmState.load(session_id)
            assert loaded.current_phase == AlgorithmPhase.GATHER
            assert "0" in loaded.phase_timestamps
            assert "started_at" in loaded.phase_timestamps["0"]
        finally:
            # Cleanup
            state = AlgorithmState.load(session_id)
            if state:
                state.state_file_path.unlink(missing_ok=True)

    @pytest.mark.e2e
    def test_phase_sequence_via_subprocess(self):
        """Test sequential phase execution via subprocess."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

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
            )
            assert result.returncode == 0

            # Manually complete GATHER for next phase
            state = AlgorithmState.load(session_id)
            state.complete_phase(0, {"gather": "done"})
            state.save()

            # Execute IDEAL_STATE via subprocess
            result = subprocess.run(
                [sys.executable, str(IDEAL_STATE_ENTRY), "--state", session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=get_subprocess_env(),
            )
            assert result.returncode == 0

            # Verify progression
            loaded = AlgorithmState.load(session_id)
            assert loaded.current_phase == AlgorithmPhase.IDEAL_STATE
        finally:
            # Cleanup
            state = AlgorithmState.load(session_id)
            if state:
                state.state_file_path.unlink(missing_ok=True)
