"""
Integration tests for loop-back scenarios.

Tests the VERIFY phase's ability to loop back to INNER_LOOP
for refinement, including iteration tracking and max iteration limits.
"""

import pytest

from orchestration.state.algorithm_state import AlgorithmState, VerificationResult
from orchestration.state.algorithm_fsm import AlgorithmPhase, AlgorithmFSM

# ============================================================================
# Helper Functions
# ============================================================================


def progress_to_verify(state: AlgorithmState) -> None:
    """Progress state through all phases to VERIFY."""
    phases = [
        AlgorithmPhase.GATHER,
        AlgorithmPhase.INTERVIEW,
        AlgorithmPhase.INNER_LOOP,
    ]
    for phase in phases:
        state.start_phase(phase)
        state.record_phase_output(phase, {phase.name.lower(): "done"})
    state.start_phase(AlgorithmPhase.VERIFY)


# ============================================================================
# Test Basic Loop-Back
# ============================================================================


class TestBasicLoopBack:
    """Tests for basic loop-back from VERIFY phase."""

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_to_inner_loop(self, mock_sessions_dir):
        """Should loop back from VERIFY to INNER_LOOP."""
        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        progress_to_verify(state)
        state.record_phase_output(
            AlgorithmPhase.VERIFY, {"verification": "failed", "needs": "refinement"}
        )

        # Loop back to INNER_LOOP
        assert state.can_loop_back()
        result = state.loop_back_to_inner_loop()

        assert result is True
        assert state.current_phase == AlgorithmPhase.INNER_LOOP
        assert state.outer_loop_iteration == 1

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_increments_outer_iteration(self, mock_sessions_dir):
        """Loop back should increment outer_loop_iteration."""
        state = AlgorithmState(user_query="Build API")

        progress_to_verify(state)
        assert state.outer_loop_iteration == 0

        # First loop back
        state.loop_back_to_inner_loop()
        assert state.outer_loop_iteration == 1

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_can_loop_back_only_from_verify(self, mock_sessions_dir):
        """can_loop_back should return False when not in VERIFY."""
        state = AlgorithmState(user_query="Build API")

        # In INITIALIZED
        assert not state.can_loop_back()

        # In GATHER
        state.start_phase(AlgorithmPhase.GATHER)
        assert not state.can_loop_back()

        # In INNER_LOOP
        state.record_phase_output(AlgorithmPhase.GATHER, {})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {})
        state.start_phase(AlgorithmPhase.INNER_LOOP)
        assert not state.can_loop_back()

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_fails_when_not_from_verify(self, mock_sessions_dir):
        """loop_back_to_inner_loop should fail when not in VERIFY."""
        state = AlgorithmState(user_query="Build API")

        # In INITIALIZED
        result = state.loop_back_to_inner_loop()
        assert result is False


# ============================================================================
# Test Iteration Tracking
# ============================================================================


class TestIterationTracking:
    """Tests for loop-back iteration counting."""

    @pytest.mark.integration
    def test_iteration_increments_on_loop_back(self, mock_sessions_dir):
        """Iteration count should increment on each loop-back."""
        state = AlgorithmState(user_query="Build API")

        progress_to_verify(state)
        assert state.outer_loop_iteration == 0

        # First loop-back
        state.loop_back_to_inner_loop()
        assert state.outer_loop_iteration == 1

    @pytest.mark.integration
    def test_multiple_loop_backs_track_iterations(self, mock_sessions_dir):
        """Multiple loop-backs should track iteration count correctly."""
        state = AlgorithmState(user_query="Build API")

        # First pass through to VERIFY
        progress_to_verify(state)

        # First loop-back
        state.loop_back_to_inner_loop()
        assert state.outer_loop_iteration == 1

        # Second pass through to VERIFY
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"iteration": 1})
        state.start_phase(AlgorithmPhase.VERIFY)

        # Second loop-back
        state.loop_back_to_inner_loop()
        assert state.outer_loop_iteration == 2

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_max_iterations_enforced(self, mock_sessions_dir):
        """Loop-back should fail at max iterations."""
        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        progress_to_verify(state)

        # Max is 3 verify iterations
        max_iterations = AlgorithmFSM.MAX_VERIFY_ITERATIONS

        for i in range(max_iterations):
            result = state.loop_back_to_inner_loop()
            assert result is True
            # Progress back to VERIFY
            state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"iteration": i + 1})
            state.start_phase(AlgorithmPhase.VERIFY)

        # Next loop-back should fail (at max)
        result = state.loop_back_to_inner_loop()
        assert result is False
        assert state.current_phase == AlgorithmPhase.VERIFY


# ============================================================================
# Test Loop-Back State Persistence
# ============================================================================


class TestLoopBackPersistence:
    """Tests for loop-back state persistence."""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_iteration_count_persists(self, mock_sessions_dir):
        """Iteration count should persist across save/load."""
        session_id = "loopback12345"
        state = AlgorithmState(user_query="Build API", session_id=session_id)

        # Progress to VERIFY
        progress_to_verify(state)

        # Loop back
        state.loop_back_to_inner_loop()
        state.save()

        # Load and verify
        loaded = AlgorithmState.load(session_id)
        assert loaded.outer_loop_iteration == 1
        assert loaded.current_phase == AlgorithmPhase.INNER_LOOP

    @pytest.mark.integration
    def test_phase_outputs_preserved_after_loop_back(self, mock_sessions_dir):
        """Phase outputs from before loop-back should be preserved."""
        session_id = "preserve12345"
        state = AlgorithmState(user_query="Build API", session_id=session_id)

        # First pass with specific outputs
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "first_pass"})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"ideal": "first_pass"})
        state.start_phase(AlgorithmPhase.INNER_LOOP)
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"work": "first_pass"})
        state.start_phase(AlgorithmPhase.VERIFY)

        # Loop back to INNER_LOOP
        state.loop_back_to_inner_loop()
        state.save()

        # Load and verify earlier outputs preserved
        loaded = AlgorithmState.load(session_id)

        # Outer loop phase outputs should be preserved
        assert loaded.phase_outputs.get("GATHER") == {"johari": "first_pass"}
        assert loaded.phase_outputs.get("INTERVIEW") == {"ideal": "first_pass"}


# ============================================================================
# Test Loop-Back Workflow Completion
# ============================================================================


class TestLoopBackWorkflowCompletion:
    """Tests for completing workflow after loop-back."""

    @pytest.mark.integration
    def test_complete_after_loop_back(self, mock_sessions_dir):
        """Should complete workflow after loop-back and re-verification."""
        state = AlgorithmState(user_query="Build API")

        # First pass
        progress_to_verify(state)
        state.add_verification_result(
            VerificationResult(
                iteration=0,
                timestamp="2026-01-27T10:00:00Z",
                status="GAPS_IDENTIFIED",
                objective_score=0.5,
                heuristic_score=0.5,
                semantic_score=0.5,
                overall_score=0.5,
                gaps=["tests failed"],
                recommendations=["fix tests"],
            )
        )

        # Loop back to INNER_LOOP
        state.loop_back_to_inner_loop()

        # Second pass from INNER_LOOP
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"pass": 2})
        state.start_phase(AlgorithmPhase.VERIFY)
        state.add_verification_result(
            VerificationResult(
                iteration=1,
                timestamp="2026-01-27T10:01:00Z",
                status="VERIFIED",
                objective_score=1.0,
                heuristic_score=1.0,
                semantic_score=1.0,
                overall_score=1.0,
                gaps=[],
                recommendations=[],
            )
        )

        # Now proceed to LEARN
        state.record_phase_output(AlgorithmPhase.VERIFY, {"verification": "passed"})
        state.start_phase(AlgorithmPhase.LEARN)
        state.record_phase_output(AlgorithmPhase.LEARN, {"learnings": "captured"})

        # Mark completed
        state.complete()
        assert state.current_phase == AlgorithmPhase.COMPLETED
        assert state.status == "completed"

        # Verify iteration tracked
        assert state.outer_loop_iteration == 1
        assert len(state.verification_history) == 2

    @pytest.mark.integration
    def test_verification_history_tracks_iterations(self, mock_sessions_dir):
        """Verification history should show results from each iteration."""
        state = AlgorithmState(user_query="Build API")

        # First pass
        progress_to_verify(state)
        state.add_verification_result(
            VerificationResult(
                iteration=0,
                timestamp="2026-01-27T10:00:00Z",
                status="GAPS_IDENTIFIED",
                objective_score=0.5,
                heuristic_score=0.5,
                semantic_score=0.5,
                overall_score=0.5,
                gaps=["iteration 0 failed"],
                recommendations=[],
            )
        )

        # Loop back
        state.loop_back_to_inner_loop()

        # Second pass
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"pass": 2})
        state.start_phase(AlgorithmPhase.VERIFY)
        state.add_verification_result(
            VerificationResult(
                iteration=1,
                timestamp="2026-01-27T10:01:00Z",
                status="VERIFIED",
                objective_score=1.0,
                heuristic_score=1.0,
                semantic_score=1.0,
                overall_score=1.0,
                gaps=[],
                recommendations=[],
            )
        )

        # Verify history
        assert len(state.verification_history) == 2
        assert state.verification_history[0].iteration == 0
        assert state.verification_history[0].status == "GAPS_IDENTIFIED"
        assert state.verification_history[1].iteration == 1
        assert state.verification_history[1].status == "VERIFIED"
