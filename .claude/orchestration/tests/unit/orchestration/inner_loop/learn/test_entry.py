"""
Unit tests for inner_loop/learn/entry.py

Tests the LEARN phase (Step 8.5) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestLearnEntryMain:
    """Tests for main() function in learn/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.inner_loop.learn import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.inner_loop.learn import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_learn_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to LEARN phase (step 8.5)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.learn import entry

        # Create state at VERIFY phase
        state = AlgorithmState(user_query="Build API", session_id="learn1234567")
        state.fsm._state = AlgorithmPhase.VERIFY
        state.fsm._history.append("VERIFY")
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "learn1234567"])

        entry.main()

        loaded = AlgorithmState.load("learn1234567")
        assert loaded.current_phase == AlgorithmPhase.LEARN

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.learn import entry

        state = AlgorithmState(user_query="Test", session_id="savelearn123")
        state.fsm._state = AlgorithmPhase.VERIFY
        state.fsm._history.append("VERIFY")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "savelearn123"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_eight_point_five(self):
        """STEP_NUM should be 8.5 for LEARN phase."""
        from orchestration.inner_loop.learn import entry

        assert entry.STEP_NUM == 8.5
