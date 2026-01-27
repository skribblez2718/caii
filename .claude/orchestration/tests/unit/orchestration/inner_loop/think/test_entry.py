"""
Unit tests for inner_loop/think/entry.py

Tests the THINK phase (Step 2) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestThinkEntryMain:
    """Tests for main() function in think/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.inner_loop.think import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.inner_loop.think import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_think_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to THINK phase (step 2)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.think import entry

        # Create state at OBSERVE phase
        state = AlgorithmState(user_query="Build API", session_id="think1234567")
        state.fsm._state = AlgorithmPhase.OBSERVE
        state.fsm._history.append("OBSERVE")
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "think1234567"])

        entry.main()

        loaded = AlgorithmState.load("think1234567")
        assert loaded.current_phase == AlgorithmPhase.THINK

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.think import entry

        state = AlgorithmState(user_query="Test", session_id="savethink123")
        state.fsm._state = AlgorithmPhase.OBSERVE
        state.fsm._history.append("OBSERVE")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "savethink123"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_two(self):
        """STEP_NUM should be 2 for THINK phase."""
        from orchestration.inner_loop.think import entry

        assert entry.STEP_NUM == 2
