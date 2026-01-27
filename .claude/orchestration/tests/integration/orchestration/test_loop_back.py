"""
Integration tests for loop-back scenarios.

Tests the VERIFY phase's ability to loop back to earlier phases
for refinement, including iteration tracking and max iteration limits.
"""

import pytest

# ============================================================================
# Test Basic Loop-Back
# ============================================================================


class TestBasicLoopBack:
    """Tests for basic loop-back from VERIFY phase."""

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_to_observe(self, mock_sessions_dir):
        """Should loop back from VERIFY to OBSERVE."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {f"step_{step}": "done"})

        state.start_phase(8)  # VERIFY
        state.complete_phase(8, {"verification": "failed", "needs": "more observation"})

        # Loop back to OBSERVE
        result = state.fsm.loop_back(AlgorithmPhase.OBSERVE)

        assert result is True
        assert state.current_phase == AlgorithmPhase.OBSERVE
        assert state.fsm.iteration_count == 1

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_to_think(self, mock_sessions_dir):
        """Should loop back from VERIFY to THINK."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Loop back to THINK
        result = state.fsm.loop_back(AlgorithmPhase.THINK)

        assert result is True
        assert state.current_phase == AlgorithmPhase.THINK

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_to_plan(self, mock_sessions_dir):
        """Should loop back from VERIFY to PLAN."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Loop back to PLAN
        result = state.fsm.loop_back(AlgorithmPhase.PLAN)

        assert result is True
        assert state.current_phase == AlgorithmPhase.PLAN

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_loop_back_to_build(self, mock_sessions_dir):
        """Should loop back from VERIFY to BUILD."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Loop back to BUILD
        result = state.fsm.loop_back(AlgorithmPhase.BUILD)

        assert result is True
        assert state.current_phase == AlgorithmPhase.BUILD


# ============================================================================
# Test Iteration Tracking
# ============================================================================


class TestIterationTracking:
    """Tests for loop-back iteration counting."""

    @pytest.mark.integration
    def test_iteration_increments_on_loop_back(self, mock_sessions_dir):
        """Iteration count should increment on each loop-back."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY
        assert state.fsm.iteration_count == 0

        # First loop-back
        state.fsm.loop_back(AlgorithmPhase.OBSERVE)
        assert state.fsm.iteration_count == 1

    @pytest.mark.integration
    def test_multiple_loop_backs_track_iterations(self, mock_sessions_dir):
        """Multiple loop-backs should track iteration count correctly."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # First pass through to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})
        state.start_phase(8)

        # First loop-back
        state.fsm.loop_back(AlgorithmPhase.OBSERVE)
        assert state.fsm.iteration_count == 1

        # Second pass through inner loop
        for step in [1, 2, 3, 4, 5]:
            state.complete_phase(step, {f"iteration_1_step_{step}": "done"})
            state.start_phase(step + 1 if step < 5 else 8)

        # Second loop-back
        state.fsm.loop_back(AlgorithmPhase.PLAN)
        assert state.fsm.iteration_count == 2

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_max_iterations_enforced(self, mock_sessions_dir):
        """Loop-back should fail at max iterations."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmFSM, AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Max is 3, so we can loop back 3 times
        max_iterations = AlgorithmFSM.MAX_ITERATIONS

        for i in range(max_iterations):
            result = state.fsm.loop_back(AlgorithmPhase.OBSERVE)
            assert result is True
            # Progress back to VERIFY
            for step in [1, 2, 3, 4, 5]:
                state.start_phase(step)
                state.complete_phase(step, {})
            state.start_phase(8)

        # Next loop-back should fail
        result = state.fsm.loop_back(AlgorithmPhase.OBSERVE)
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
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "loopback12345"
        state = AlgorithmState(user_query="Build API", session_id=session_id)

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Loop back
        state.fsm.loop_back(AlgorithmPhase.OBSERVE)
        state.save()

        # Load and verify
        loaded = AlgorithmState.load(session_id)
        assert loaded.fsm.iteration_count == 1
        assert loaded.current_phase == AlgorithmPhase.OBSERVE

    @pytest.mark.integration
    def test_phase_outputs_preserved_after_loop_back(self, mock_sessions_dir):
        """Phase outputs from before loop-back should be preserved."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "preserve12345"
        state = AlgorithmState(user_query="Build API", session_id=session_id)

        # First pass with specific outputs
        outputs = {
            0: {"johari": "first_pass"},
            0.5: {"ideal": "first_pass"},
            1: {"observe": "first_pass"},
            2: {"think": "first_pass"},
            3: {"plan": "first_pass"},
            4: {"build": "first_pass"},
            5: {"execute": "first_pass"},
        }

        for step, output in outputs.items():
            state.start_phase(step)
            state.complete_phase(step, output)

        state.start_phase(8)  # VERIFY

        # Loop back to PLAN
        state.fsm.loop_back(AlgorithmPhase.PLAN)
        state.save()

        # Load and verify earlier outputs preserved
        loaded = AlgorithmState.load(session_id)

        # Steps 0, 0.5, 1, 2 should still have their outputs
        assert loaded.phase_outputs.get("0") == {"johari": "first_pass"}
        assert loaded.phase_outputs.get("0.5") == {"ideal": "first_pass"}
        assert loaded.phase_outputs.get("1") == {"observe": "first_pass"}
        assert loaded.phase_outputs.get("2") == {"think": "first_pass"}


# ============================================================================
# Test Loop-Back Workflow Completion
# ============================================================================


class TestLoopBackWorkflowCompletion:
    """Tests for completing workflow after loop-back."""

    @pytest.mark.integration
    def test_complete_after_loop_back(self, mock_sessions_dir):
        """Should complete workflow after loop-back and re-verification."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # First pass
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {f"step_{step}": "pass_1"})

        state.start_phase(8)  # VERIFY
        state.add_verification_result({"check": "tests"}, passed=False)

        # Loop back to BUILD
        state.fsm.loop_back(AlgorithmPhase.BUILD)

        # Second pass from BUILD
        for step in [4, 5]:
            state.complete_phase(step, {f"step_{step}": "pass_2"})
            if step < 5:
                state.start_phase(5)

        state.start_phase(8)  # VERIFY again
        state.add_verification_result({"check": "tests"}, passed=True)

        # Now proceed to LEARN
        state.complete_phase(8, {"verification": "passed"})
        state.start_phase(8.5)  # LEARN
        state.complete_phase(8.5, {"learnings": "captured"})

        # Mark completed
        assert state.mark_completed()
        assert state.current_phase == AlgorithmPhase.COMPLETED
        assert state.status == "completed"

        # Verify iteration tracked
        assert state.fsm.iteration_count == 1
        assert len(state.verification_results) == 2

    @pytest.mark.integration
    def test_verification_history_tracks_iterations(self, mock_sessions_dir):
        """Verification history should show results from each iteration."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # First pass
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)
        state.add_verification_result({"check": "iteration_0"}, passed=False)

        # Loop back
        state.fsm.loop_back(AlgorithmPhase.OBSERVE)

        # Second pass
        for step in [1, 2, 3, 4, 5]:
            state.complete_phase(step, {})
            if step < 5:
                state.start_phase(step + 1)

        state.start_phase(8)
        state.add_verification_result({"check": "iteration_1"}, passed=True)

        # Verify history
        assert len(state.verification_results) == 2
        assert state.verification_results[0]["iteration"] == 0
        assert state.verification_results[0]["passed"] is False
        assert state.verification_results[1]["iteration"] == 1
        assert state.verification_results[1]["passed"] is True
