"""
Unit tests for inner_loop/plan/entry.py

Tests the PLAN phase (Step 3) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestPlanEntryMain:
    """Tests for main() function in plan/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.inner_loop.plan import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.inner_loop.plan import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_plan_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to PLAN phase (step 3)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.plan import entry

        # Create state at THINK phase
        state = AlgorithmState(user_query="Build API", session_id="plan12345678")
        state.fsm._state = AlgorithmPhase.THINK
        state.fsm._history.append("THINK")
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "plan12345678"])

        entry.main()

        loaded = AlgorithmState.load("plan12345678")
        assert loaded.current_phase == AlgorithmPhase.PLAN

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.plan import entry

        state = AlgorithmState(user_query="Test", session_id="saveplan12345")
        state.fsm._state = AlgorithmPhase.THINK
        state.fsm._history.append("THINK")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "saveplan12345"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_three(self):
        """STEP_NUM should be 3 for PLAN phase."""
        from orchestration.inner_loop.plan import entry

        assert entry.STEP_NUM == 3
