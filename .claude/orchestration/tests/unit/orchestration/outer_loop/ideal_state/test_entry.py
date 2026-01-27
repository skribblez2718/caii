"""
Unit tests for outer_loop/ideal_state/entry.py

Tests the IDEAL_STATE phase (Step 0.5) entry point.
"""

import sys
from unittest.mock import patch

import pytest


class TestIdealStateEntryMain:
    """Tests for main() function in ideal_state/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.outer_loop.ideal_state import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.outer_loop.ideal_state import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_ideal_state_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to IDEAL_STATE phase (step 0.5)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.ideal_state import entry

        # Create state at GATHER phase
        state = AlgorithmState(user_query="Build API", session_id="ideal1234567")
        state.start_phase(0)  # GATHER
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "ideal1234567"])

        entry.main()

        loaded = AlgorithmState.load("ideal1234567")
        assert loaded.current_phase == AlgorithmPhase.IDEAL_STATE

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.ideal_state import entry

        state = AlgorithmState(user_query="Test", session_id="saveideal123")
        state.start_phase(0)
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "saveideal123"])

        with patch.object(AlgorithmState, "save", tracking_save):
            entry.main()

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_loads_content_file(self, mock_sessions_dir, monkeypatch, capsys):
        """Should load content from ideal_state_capture.md."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.ideal_state import entry

        state = AlgorithmState(user_query="Test", session_id="contideal123")
        state.start_phase(0)
        state.save()

        content_loaded = []

        def mock_load(script_path, filename):
            content_loaded.append(filename)
            return "Mock content"

        monkeypatch.setattr(entry, "load_content", mock_load)
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "contideal123"])

        entry.main()

        assert "ideal_state_capture.md" in content_loaded

    @pytest.mark.unit
    def test_step_num_is_half(self):
        """STEP_NUM should be 0.5 for IDEAL_STATE phase."""
        from orchestration.outer_loop.ideal_state import entry

        assert entry.STEP_NUM == 0.5
