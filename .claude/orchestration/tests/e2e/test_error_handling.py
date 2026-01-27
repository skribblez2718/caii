"""
End-to-end tests for error handling and edge cases.

Tests system behavior under error conditions, invalid inputs,
and boundary cases to ensure robust error handling.
"""

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
OBSERVE_ENTRY = ORCHESTRATION_ROOT / "inner_loop" / "observe" / "entry.py"


# ============================================================================
# Test Invalid State Handling
# ============================================================================


class TestInvalidStateHandling:
    """Tests for handling invalid state scenarios."""

    @pytest.mark.e2e
    def test_load_nonexistent_session(self, mock_sessions_dir):
        """Loading non-existent session should return None."""
        from orchestration.state import AlgorithmState

        state = AlgorithmState.load("nonexistent12")
        assert state is None

    @pytest.mark.e2e
    def test_phase_entry_rejects_invalid_session(self):
        """Phase entry points should reject invalid session IDs."""
        result = subprocess.run(
            [sys.executable, str(GATHER_ENTRY), "--state", "invalid12345"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 1
        assert "not found" in result.stderr.lower()

    @pytest.mark.e2e
    def test_phase_entry_handles_corrupted_state(self, mock_sessions_dir):
        """Phase entry should handle corrupted state file gracefully."""
        from orchestration.state import config as state_config

        # Create a corrupted state file
        session_id = "corrupt12345"
        state_file = state_config.SESSIONS_DIR / f"algorithm-{session_id}.json"
        state_file.write_text("{ invalid json }")

        result = subprocess.run(
            [sys.executable, str(GATHER_ENTRY), "--state", session_id],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail gracefully
        assert result.returncode == 1


# ============================================================================
# Test Invalid Transition Handling
# ============================================================================


class TestInvalidTransitionHandling:
    """Tests for handling invalid state transitions."""

    @pytest.mark.e2e
    def test_skip_phase_rejected(self, mock_sessions_dir):
        """Skipping a required phase should be rejected."""
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="Skip phase test")

        # Try to skip GATHER (0) and go directly to IDEAL_STATE (0.5)
        result = state.start_phase(0.5)

        assert result is False
        # Should still be in INITIALIZED
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        assert state.current_phase == AlgorithmPhase.INITIALIZED

    @pytest.mark.e2e
    def test_backward_transition_rejected(self, mock_sessions_dir):
        """Going backward in phases (without loop-back) should be rejected."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Backward test")

        # Progress to OBSERVE
        state.start_phase(0)
        state.complete_phase(0, {})
        state.start_phase(0.5)
        state.complete_phase(0.5, {})
        state.start_phase(1)  # OBSERVE

        assert state.current_phase == AlgorithmPhase.OBSERVE

        # Try to go back to GATHER
        result = state.start_phase(0)

        assert result is False
        assert state.current_phase == AlgorithmPhase.OBSERVE

    @pytest.mark.e2e
    def test_double_start_phase(self, mock_sessions_dir):
        """Starting the same phase twice should fail."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Double start test")

        # Start GATHER
        result1 = state.start_phase(0)
        assert result1 is True
        assert state.current_phase == AlgorithmPhase.GATHER

        # Try to start GATHER again
        result2 = state.start_phase(0)
        assert result2 is False  # Already in GATHER


# ============================================================================
# Test Completion Validation
# ============================================================================


class TestCompletionValidation:
    """Tests for completion validation logic."""

    @pytest.mark.e2e
    def test_cannot_complete_from_wrong_phase(self, mock_sessions_dir):
        """mark_completed should fail if not in LEARN phase."""
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="Wrong phase completion")

        # Try to complete from INITIALIZED
        result = state.mark_completed()
        assert result is False
        assert state.status != "completed"

    @pytest.mark.e2e
    def test_cannot_complete_from_verify(self, mock_sessions_dir):
        """mark_completed should fail from VERIFY phase."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Verify completion test")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY
        assert state.current_phase == AlgorithmPhase.VERIFY

        # Try to complete
        result = state.mark_completed()
        assert result is False
        assert state.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.e2e
    def test_completed_state_is_terminal(self, mock_sessions_dir):
        """COMPLETED state should be terminal - no transitions allowed."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Terminal state test")

        # Progress to LEARN
        for step in [0, 0.5, 1, 2, 3, 4, 5, 8]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8.5)
        state.complete_phase(8.5, {})
        state.mark_completed()

        assert state.current_phase == AlgorithmPhase.COMPLETED

        # Try any transition
        result = state.start_phase(0)  # Try to start over
        assert result is False
        assert state.current_phase == AlgorithmPhase.COMPLETED


# ============================================================================
# Test Loop-Back Constraints
# ============================================================================


class TestLoopBackConstraints:
    """Tests for loop-back constraint enforcement."""

    @pytest.mark.e2e
    def test_loop_back_only_from_verify(self, mock_sessions_dir):
        """Loop-back should only work from VERIFY phase."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Loop-back constraint test")

        # Progress to PLAN (not VERIFY)
        for step in [0, 0.5, 1, 2]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(3)  # PLAN
        assert state.current_phase == AlgorithmPhase.PLAN

        # Try loop-back from PLAN
        result = state.fsm.loop_back(AlgorithmPhase.OBSERVE)
        assert result is False
        assert state.current_phase == AlgorithmPhase.PLAN

    @pytest.mark.e2e
    def test_loop_back_to_invalid_target(self, mock_sessions_dir):
        """Loop-back to invalid target phases should fail."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Invalid loop-back target")

        # Progress to VERIFY
        for step in [0, 0.5, 1, 2, 3, 4, 5]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Try loop-back to GATHER (not allowed)
        result = state.fsm.loop_back(AlgorithmPhase.GATHER)
        assert result is False

        # Try loop-back to IDEAL_STATE (not allowed)
        result = state.fsm.loop_back(AlgorithmPhase.IDEAL_STATE)
        assert result is False

        assert state.current_phase == AlgorithmPhase.VERIFY


# ============================================================================
# Test Halt Constraints
# ============================================================================


class TestHaltConstraints:
    """Tests for halt state constraint enforcement."""

    @pytest.mark.e2e
    def test_cannot_halt_from_completed(self, mock_sessions_dir):
        """Cannot halt from COMPLETED state."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Halt from completed test")

        # Progress to completion
        for step in [0, 0.5, 1, 2, 3, 4, 5, 8, 8.5]:
            state.start_phase(step)
            state.complete_phase(step, {})
        state.mark_completed()

        assert state.current_phase == AlgorithmPhase.COMPLETED

        # Try to halt
        result = state.halt_for_clarification("Late question", ["?"])
        assert result is False
        assert state.current_phase == AlgorithmPhase.COMPLETED

    @pytest.mark.e2e
    def test_resume_requires_halted_state(self, mock_sessions_dir):
        """resume_from_halt should fail if not in HALTED state."""
        from orchestration.state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Resume without halt test")
        state.start_phase(0)

        assert state.current_phase == AlgorithmPhase.GATHER

        # Try to resume without being halted
        result = state.resume_from_halt(0, {"answer": "test"})
        assert result is False


# ============================================================================
# Test Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.e2e
    def test_empty_user_query(self, mock_sessions_dir):
        """Should handle empty user query."""
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="")
        state.save()

        loaded = AlgorithmState.load(state.session_id)
        assert loaded.user_query == ""

    @pytest.mark.e2e
    def test_very_long_user_query(self, mock_sessions_dir):
        """Should handle very long user queries."""
        from orchestration.state import AlgorithmState

        long_query = "Build an API " * 1000  # ~13000 characters
        state = AlgorithmState(user_query=long_query)
        state.save()

        loaded = AlgorithmState.load(state.session_id)
        assert loaded.user_query == long_query

    @pytest.mark.e2e
    def test_special_characters_in_query(self, mock_sessions_dir):
        """Should handle special characters in user query."""
        from orchestration.state import AlgorithmState

        special_query = 'Build an API with "quotes" and <brackets> & symbols'
        state = AlgorithmState(user_query=special_query)
        state.save()

        loaded = AlgorithmState.load(state.session_id)
        assert loaded.user_query == special_query

    @pytest.mark.e2e
    def test_unicode_in_query(self, mock_sessions_dir):
        """Should handle Unicode characters in user query."""
        from orchestration.state import AlgorithmState

        unicode_query = "Build an API für 日本語 with émojis 🚀"
        state = AlgorithmState(user_query=unicode_query)
        state.save()

        loaded = AlgorithmState.load(state.session_id)
        assert loaded.user_query == unicode_query

    @pytest.mark.e2e
    def test_many_phase_outputs(self, mock_sessions_dir):
        """Should handle large amounts of phase output data."""
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="Large output test")

        for step in [0, 0.5, 1, 2, 3, 4, 5, 8, 8.5]:
            state.start_phase(step)
            large_output = {
                "data": "x" * 10000,
                "list": list(range(1000)),
                "nested": {"a": {"b": {"c": "deep"}}},
            }
            state.complete_phase(step, large_output)

        state.save()

        loaded = AlgorithmState.load(state.session_id)
        assert len(loaded.phase_outputs) == 9
        assert loaded.phase_outputs["0"]["data"] == "x" * 10000
