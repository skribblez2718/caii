"""
Unit tests for decompose/entry.py (stub implementation)

Tests the decompose protocol entry point:
- Requires --state argument
- Exits for invalid session
- Prints stub message with complexity and query
"""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

# ============================================================================
# TestDecomposeEntry
# ============================================================================


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
    def test_decompose_entry_loads_state_and_prints_stub(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should load state and print stub message."""
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

        # Verify stub output contains expected information
        assert "DECOMPOSE" in captured.out
        assert "complex" in captured.out.lower()
        assert "Complex refactoring task" in captured.out

    @pytest.mark.unit
    def test_decompose_entry_prints_stub_for_very_complex(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point should print stub message for very_complex task."""
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

        # Verify stub output
        assert "DECOMPOSE" in captured.out
        assert (
            "very_complex" in captured.out.lower()
            or "very complex" in captured.out.lower()
        )

    @pytest.mark.unit
    def test_decompose_entry_mentions_todo(
        self, mock_sessions_dir, monkeypatch, capsys
    ):
        """Entry point stub should mention TODO for future implementation."""
        from orchestration.decompose import entry as decompose_entry
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(
            user_query="Test query", session_id="todo_test123", complexity="complex"
        )
        state.save()

        monkeypatch.setattr(sys, "argv", ["entry.py", "--state", "todo_test123"])

        decompose_entry.main()

        captured = capsys.readouterr()

        # Stub should indicate it's not implemented yet
        assert "TODO" in captured.out or "STUB" in captured.out
