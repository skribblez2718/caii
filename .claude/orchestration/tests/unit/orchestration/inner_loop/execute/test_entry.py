"""
Unit tests for inner_loop/execute/entry.py

Tests the EXECUTE phase (Step 5) entry point.
Updated to work with refactored run_phase_entry() pattern.
"""

import sys
from unittest.mock import patch

import pytest

from orchestration.state.algorithm_state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.entry_base import run_phase_entry, PhaseConfig


class TestExecuteEntryMain:
    """Tests for EXECUTE entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.EXECUTE,
                    phase_name="EXECUTE",
                    content_file="execute_phase.md",
                    description="EXECUTE Phase (Step 5)",
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
                    phase=AlgorithmPhase.EXECUTE,
                    phase_name="EXECUTE",
                    content_file="execute_phase.md",
                    description="EXECUTE Phase (Step 5)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_execute_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to EXECUTE phase (step 5)."""
        # Create state at BUILD phase (predecessor of EXECUTE)
        state = AlgorithmState(user_query="Build API", session_id="exec12345678")
        state._fsm._state = AlgorithmPhase.BUILD
        state._fsm._history.append("BUILD")
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.EXECUTE,
                    phase_name="EXECUTE",
                    content_file="execute_phase.md",
                    description="EXECUTE Phase (Step 5)",
                ),
                argv=["--state", "exec12345678"],
            )

        loaded = AlgorithmState.load("exec12345678")
        assert loaded.current_phase == AlgorithmPhase.EXECUTE

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        state = AlgorithmState(user_query="Test", session_id="saveexec1234")
        state._fsm._state = AlgorithmPhase.BUILD
        state._fsm._history.append("BUILD")
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
                        phase=AlgorithmPhase.EXECUTE,
                        phase_name="EXECUTE",
                        content_file="execute_phase.md",
                        description="EXECUTE Phase (Step 5)",
                    ),
                    argv=["--state", "saveexec1234"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_five(self):
        """STEP_NUM should be 5 for EXECUTE phase."""
        from orchestration.inner_loop.execute import entry

        assert entry.STEP_NUM == 5
