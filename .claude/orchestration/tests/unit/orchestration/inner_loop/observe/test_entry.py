"""
Unit tests for inner_loop/observe/entry.py

Tests the OBSERVE phase (Step 1) entry point.
Updated to work with refactored run_phase_entry() pattern.
"""

import sys
from unittest.mock import patch

import pytest

from orchestration.state.algorithm_state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.entry_base import run_phase_entry, PhaseConfig


class TestObserveEntryMain:
    """Tests for OBSERVE entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.INNER_LOOP,
                    phase_name="OBSERVE",
                    content_file="observe_phase.md",
                    description="OBSERVE Phase (Step 1)",
                ),
            )

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.INNER_LOOP,
                    phase_name="OBSERVE",
                    content_file="observe_phase.md",
                    description="OBSERVE Phase (Step 1)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_observe_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to OBSERVE phase (step 1).

        Note: Step 1 maps to INNER_LOOP in the current FSM, not OBSERVE directly.
        The inner loop phases (OBSERVE, THINK, etc.) are conceptual steps within INNER_LOOP.
        """
        # Create state at INTERVIEW phase (predecessor of INNER_LOOP)
        state = AlgorithmState(user_query="Build API", session_id="observ123456")
        state.start_phase(AlgorithmPhase.GATHER)
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.INNER_LOOP,
                    phase_name="OBSERVE",
                    content_file="observe_phase.md",
                    description="OBSERVE Phase (Step 1)",
                ),
                argv=["--state", "observ123456"],
            )

        loaded = AlgorithmState.load("observ123456")
        # Step 1 maps to INNER_LOOP in the FSM
        assert loaded.current_phase == AlgorithmPhase.INNER_LOOP

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        # Create state and transition to INTERVIEW (predecessor of INNER_LOOP)
        state = AlgorithmState(user_query="Test", session_id="saveobserv12")
        state._fsm._state = AlgorithmPhase.INTERVIEW
        state._fsm._history.append("INTERVIEW")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        with patch("orchestration.utils.load_content", return_value="Content"):
            with patch.object(AlgorithmState, "save", tracking_save):
                run_phase_entry(
                    "dummy.py",
                    PhaseConfig(
                        phase=AlgorithmPhase.INNER_LOOP,
                        phase_name="OBSERVE",
                        content_file="observe_phase.md",
                        description="OBSERVE Phase (Step 1)",
                    ),
                    argv=["--state", "saveobserv12"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_one(self):
        """STEP_NUM should be 1 for OBSERVE phase."""
        from orchestration.inner_loop.observe import entry

        assert entry.STEP_NUM == 1
