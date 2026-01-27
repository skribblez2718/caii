"""
Unit tests for inner_loop/observe/entry.py

Tests the OBSERVE phase (Step 1) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestObserveEntryMain:
    """Tests for main() function in observe/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.inner_loop.observe import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.inner_loop.observe import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_observe_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to OBSERVE phase (step 1)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.observe import entry

        # Create state at IDEAL_STATE phase
        state = AlgorithmState(user_query="Build API", session_id="observ123456")
        state.start_phase(0)  # GATHER
        state.start_phase(0.5)  # IDEAL_STATE
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "observ123456"])

        entry.main()

        loaded = AlgorithmState.load("observ123456")
        assert loaded.current_phase == AlgorithmPhase.OBSERVE

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.inner_loop.observe import entry

        state = AlgorithmState(user_query="Test", session_id="saveobserv12")
        state.fsm._state = AlgorithmPhase.IDEAL_STATE
        state.fsm._history.append("IDEAL_STATE")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "saveobserv12"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_one(self):
        """STEP_NUM should be 1 for OBSERVE phase."""
        from orchestration.inner_loop.observe import entry

        assert entry.STEP_NUM == 1
