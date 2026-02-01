"""
Unit tests for outer_loop/ideal_state/entry.py

Tests the IDEAL_STATE/INTERVIEW phase (Step 0.5) entry point.
Updated to work with refactored run_phase_entry() pattern.

Note: Step 0.5 maps to INTERVIEW phase in the FSM.
IDEAL_STATE is a legacy alias for INTERVIEW.
"""

import sys
from unittest.mock import patch

import pytest

from orchestration.state.algorithm_state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.entry_base import run_phase_entry, PhaseConfig


class TestIdealStateEntryMain:
    """Tests for IDEAL_STATE/INTERVIEW entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.INTERVIEW,
                    phase_name="IDEAL_STATE",
                    content_file="ideal_state_capture.md",
                    description="IDEAL STATE Phase (Step 0.5)",
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
                    phase=AlgorithmPhase.INTERVIEW,
                    phase_name="IDEAL_STATE",
                    content_file="ideal_state_capture.md",
                    description="IDEAL STATE Phase (Step 0.5)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_ideal_state_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to INTERVIEW phase (step 0.5)."""
        # Create state at GATHER phase (predecessor of INTERVIEW)
        state = AlgorithmState(user_query="Build API", session_id="ideal1234567")
        state.start_phase(AlgorithmPhase.GATHER)
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.INTERVIEW,
                    phase_name="IDEAL_STATE",
                    content_file="ideal_state_capture.md",
                    description="IDEAL STATE Phase (Step 0.5)",
                ),
                argv=["--state", "ideal1234567"],
            )

        loaded = AlgorithmState.load("ideal1234567")
        # Step 0.5 maps to INTERVIEW in the FSM
        assert loaded.current_phase == AlgorithmPhase.INTERVIEW

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        # Create state at GATHER phase (predecessor of INTERVIEW)
        state = AlgorithmState(user_query="Test", session_id="saveideal123")
        state.start_phase(AlgorithmPhase.GATHER)
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
                        phase=AlgorithmPhase.INTERVIEW,
                        phase_name="IDEAL_STATE",
                        content_file="ideal_state_capture.md",
                        description="IDEAL STATE Phase (Step 0.5)",
                    ),
                    argv=["--state", "saveideal123"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_half(self):
        """STEP_NUM should be 0.5 for IDEAL_STATE phase."""
        from orchestration.outer_loop.ideal_state import entry

        assert entry.STEP_NUM == 0.5
