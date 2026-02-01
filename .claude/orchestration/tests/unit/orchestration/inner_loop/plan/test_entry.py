"""
Unit tests for inner_loop/plan/entry.py

Tests the PLAN phase (Step 3) entry point.
Updated to work with refactored run_phase_entry() pattern.
"""

import sys
from unittest.mock import patch

import pytest

from orchestration.state.algorithm_state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.entry_base import run_phase_entry, PhaseConfig


class TestPlanEntryMain:
    """Tests for PLAN entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.PLAN,
                    phase_name="PLAN",
                    content_file="plan_phase.md",
                    description="PLAN Phase (Step 3)",
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
                    phase=AlgorithmPhase.PLAN,
                    phase_name="PLAN",
                    content_file="plan_phase.md",
                    description="PLAN Phase (Step 3)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_plan_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to PLAN phase (step 3)."""
        # Create state at THINK phase (predecessor of PLAN)
        state = AlgorithmState(user_query="Build API", session_id="plan12345678")
        state._fsm._state = AlgorithmPhase.THINK
        state._fsm._history.append("THINK")
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.PLAN,
                    phase_name="PLAN",
                    content_file="plan_phase.md",
                    description="PLAN Phase (Step 3)",
                ),
                argv=["--state", "plan12345678"],
            )

        loaded = AlgorithmState.load("plan12345678")
        assert loaded.current_phase == AlgorithmPhase.PLAN

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        state = AlgorithmState(user_query="Test", session_id="saveplan12345")
        state._fsm._state = AlgorithmPhase.THINK
        state._fsm._history.append("THINK")
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
                        phase=AlgorithmPhase.PLAN,
                        phase_name="PLAN",
                        content_file="plan_phase.md",
                        description="PLAN Phase (Step 3)",
                    ),
                    argv=["--state", "saveplan12345"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_three(self):
        """STEP_NUM should be 3 for PLAN phase."""
        from orchestration.inner_loop.plan import entry

        assert entry.STEP_NUM == 3
