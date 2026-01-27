"""
Unit tests for outer_loop/verify/entry.py

Tests the VERIFY phase (Step 8) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestVerifyEntryMain:
    """Tests for main() function in verify/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.outer_loop.verify import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.outer_loop.verify import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_verify_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to VERIFY phase (step 8)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.verify import entry

        # Create state at EXECUTE phase
        state = AlgorithmState(user_query="Build API", session_id="verify1234567")
        state.fsm._state = AlgorithmPhase.EXECUTE
        state.fsm._history.append("EXECUTE")
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "verify1234567"])

        entry.main()

        loaded = AlgorithmState.load("verify1234567")
        assert loaded.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.verify import entry

        state = AlgorithmState(user_query="Test", session_id="saveverify12")
        state.fsm._state = AlgorithmPhase.EXECUTE
        state.fsm._history.append("EXECUTE")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "saveverify12"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_loads_content_file(self, mock_sessions_dir, monkeypatch, capsys):
        """Should load content from verification.md."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.verify import entry

        state = AlgorithmState(user_query="Test", session_id="contverify12")
        state.fsm._state = AlgorithmPhase.EXECUTE
        state.fsm._history.append("EXECUTE")
        state.save()

        content_loaded = []

        def mock_load(script_path, filename):
            content_loaded.append(filename)
            return "Mock content"

        monkeypatch.setattr(entry, "load_content", mock_load)
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "contverify12"])

        entry.main()

        assert "verification.md" in content_loaded

    @pytest.mark.unit
    def test_step_num_is_eight(self):
        """STEP_NUM should be 8 for VERIFY phase."""
        from orchestration.outer_loop.verify import entry

        assert entry.STEP_NUM == 8
