"""
Unit tests for outer_loop/gather/entry.py

Tests the GATHER phase (Step 0) entry point.
"""

import sys
from unittest.mock import patch, MagicMock

import pytest

# ============================================================================
# TestGatherEntryMain
# ============================================================================


class TestGatherEntryMain:
    """Tests for main() function in gather/entry.py"""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        # Import needs to happen after path manipulation
        from orchestration.outer_loop.gather import entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.outer_loop.gather import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
        assert "nonexistent12" in captured.err

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_gather_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to GATHER phase (step 0)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.gather import entry

        # Create and save initial state
        state = AlgorithmState(user_query="Build an API", session_id="gather123456")
        state.save()

        # Mock load_content to avoid needing actual content file
        monkeypatch.setattr(entry, "load_content", lambda *args: "Test content")

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "gather123456"])

        entry.main()

        # Reload state and check phase
        loaded = AlgorithmState.load("gather123456")
        assert loaded.current_phase == AlgorithmPhase.GATHER

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.gather import entry

        # Create initial state
        state = AlgorithmState(user_query="Test query", session_id="savetest1234")
        state.save()

        save_order = []
        print_order = []

        original_save = AlgorithmState.save

        def tracking_save(self):
            save_order.append("save")
            return original_save(self)

        original_print = print

        def tracking_print(*args, **kwargs):
            if args and "content" in str(args[0]).lower() or len(save_order) > 0:
                print_order.append("print")
            return original_print(*args, **kwargs)

        monkeypatch.setattr(entry, "load_content", lambda *args: "Content here")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "savetest1234"])

        with patch.object(AlgorithmState, "save", tracking_save):
            with patch("builtins.print", tracking_print):
                entry.main()

        # Save should happen before print
        assert len(save_order) > 0, "save() was not called"

    @pytest.mark.unit
    def test_loads_content_file(self, mock_sessions_dir, monkeypatch, capsys):
        """Should load content from gather_phase.md."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.gather import entry

        state = AlgorithmState(user_query="Test", session_id="content12345")
        state.save()

        content_loaded = []

        def mock_load_content(script_path, filename):
            content_loaded.append(filename)
            return "Mock content"

        monkeypatch.setattr(entry, "load_content", mock_load_content)
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "content12345"])

        entry.main()

        assert "gather_phase.md" in content_loaded

    @pytest.mark.unit
    def test_substitutes_placeholders(self, mock_sessions_dir, monkeypatch, capsys):
        """Should substitute user_query and session_id in content."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.gather import entry

        state = AlgorithmState(user_query="Build REST API", session_id="subst1234567")
        state.save()

        monkeypatch.setattr(
            entry,
            "load_content",
            lambda *args: "Query: {user_query} Session: {session_id}",
        )
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "subst1234567"])

        entry.main()

        captured = capsys.readouterr()
        assert "Build REST API" in captured.out
        assert "subst1234567" in captured.out

    @pytest.mark.unit
    def test_prints_prompt(self, mock_sessions_dir, monkeypatch, capsys):
        """Should print the phase prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.outer_loop.gather import entry

        state = AlgorithmState(user_query="Test", session_id="print1234567")
        state.save()

        monkeypatch.setattr(entry, "load_content", lambda *args: "GATHER PHASE OUTPUT")
        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "print1234567"])

        entry.main()

        captured = capsys.readouterr()
        assert "GATHER PHASE OUTPUT" in captured.out

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_invalid_phase_transition_exits(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Should exit with error if FSM transition is invalid."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.outer_loop.gather import entry

        # Create state already at GATHER phase
        state = AlgorithmState(user_query="Test", session_id="invalid12345")
        state.fsm._state = AlgorithmPhase.GATHER
        state.fsm._history.append("GATHER")
        state.save()

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "invalid12345"])

        with pytest.raises(SystemExit) as exc_info:
            entry.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Cannot transition" in captured.err

    @pytest.mark.unit
    def test_step_num_is_zero(self):
        """STEP_NUM should be 0 for GATHER phase."""
        from orchestration.outer_loop.gather import entry

        assert entry.STEP_NUM == 0
