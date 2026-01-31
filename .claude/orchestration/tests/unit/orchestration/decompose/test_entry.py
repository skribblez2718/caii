"""
Unit tests for decompose/entry.py

Tests the decompose protocol entry point:
- Requires --state argument
- Exits for invalid session
- Loads state and triggers agent flow
- Legacy mode (--no-flow) prints status
"""

import sys

import pytest


class TestDecomposeEntry:
    """Tests for decompose protocol entry point."""

    @pytest.mark.unit
    def test_decompose_entry_requires_state_arg(self, monkeypatch, capsys):
        """Entry point should require --state argument."""
        from orchestration.decompose import entry as decompose_entry

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            decompose_entry.main()

        assert exc_info.value.code != 0
        captured = capsys.readouterr()
        assert "required" in captured.err.lower() or "error" in captured.stderr.lower()

    @pytest.mark.unit
    def test_decompose_entry_exits_for_invalid_session(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should exit with error for non-existent session."""
        from orchestration.decompose import entry as decompose_entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "nonexistent12"])

        with pytest.raises(SystemExit) as exc_info:
            decompose_entry.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower()

    @pytest.mark.unit
    def test_decompose_entry_loads_state_and_prints_header(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should load state and print protocol header."""
        from orchestration.decompose import entry as decompose_entry
        from orchestration.state.algorithm_state import AlgorithmState

        # Create a valid state
        state = AlgorithmState(
            user_query="Complex refactoring task",
            session_id="decomp12345",
            complexity="complex",
        )
        state.save()

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "decomp12345"])

        # Should not raise (exit code 0)
        decompose_entry.main()

        captured = capsys.readouterr()

        # Verify output contains expected information
        assert "DECOMPOSE" in captured.out
        assert "complex" in captured.out.lower()
        assert "Complex refactoring task" in captured.out

    @pytest.mark.unit
    def test_decompose_entry_prints_flow_info_for_very_complex(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should print flow info for very_complex task."""
        from orchestration.decompose import entry as decompose_entry
        from orchestration.state.algorithm_state import AlgorithmState

        # Create a very_complex state
        state = AlgorithmState(
            user_query="System-wide architecture change",
            session_id="verycomp123",
            complexity="very_complex",
        )
        state.save()

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "verycomp123"])

        decompose_entry.main()

        captured = capsys.readouterr()

        # Verify output shows flow info
        assert "DECOMPOSE" in captured.out
        assert (
            "very_complex" in captured.out.lower()
            or "very complex" in captured.out.lower()
        )
        # Should show flow info (not stub)
        assert "decompose-protocol" in captured.out or "Flow" in captured.out

    @pytest.mark.unit
    def test_decompose_entry_triggers_agent_flow(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should trigger agent flow (not stub)."""
        from orchestration.decompose import entry as decompose_entry
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(
            user_query="Test query", session_id="flow_test123", complexity="complex"
        )
        state.save()

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "flow_test123"])

        decompose_entry.main()

        captured = capsys.readouterr()

        # Should show flow invocation, not stub message
        assert "MANDATORY" in captured.out or "Task tool" in captured.out
        assert "clarification" in captured.out

    @pytest.mark.unit
    def test_decompose_entry_no_flow_mode(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point with --no-flow should print legacy status."""
        from orchestration.decompose import entry as decompose_entry
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(
            user_query="Legacy test", session_id="legacy123456", complexity="complex"
        )
        state.save()

        monkeypatch.setattr(
            sys, "argv", ["entry.py", "--state", "legacy123456", "--no-flow"]
        )

        decompose_entry.main()

        captured = capsys.readouterr()

        # Should show legacy status, not flow invocation
        assert "Protocol Status" in captured.out or "Expected Behavior" in captured.out
        assert "MANDATORY" not in captured.out
