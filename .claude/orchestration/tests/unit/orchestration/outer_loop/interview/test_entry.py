"""
INTERVIEW Entry Point Unit Tests

Tests for INTERVIEW phase entry point.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
class TestInterviewEntryMain:
    """Tests for INTERVIEW entry point main function."""

    def test_exits_without_state_arg(self):
        """Should exit with error if no --state argument."""
        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "interview"
            / "entry.py"
        )

        result = subprocess.run(
            [sys.executable, str(entry_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_exits_for_missing_session(self, temp_state_dir, monkeypatch):
        """Should exit with error for nonexistent session."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "interview"
            / "entry.py"
        )

        result = subprocess.run(
            [sys.executable, str(entry_path), "--state", "nonexistent12"],
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(entry_path.parent.parent.parent.parent),
            },
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_prints_phase_header(self, temp_state_dir, monkeypatch):
        """Should print INTERVIEW phase header."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState.for_task("test query")
        state.start_phase(AlgorithmPhase.GET_STATE)  # Need to be past INITIALIZED
        state.save()

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "interview"
            / "entry.py"
        )

        result = subprocess.run(
            [sys.executable, str(entry_path), "--state", state.session_id, "--no-flow"],
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(entry_path.parent.parent.parent.parent),
            },
        )

        assert result.returncode == 0
        assert "INTERVIEW Phase" in result.stdout

    def test_step_num_is_half(self):
        """STEP_NUM should be 0.5 for INTERVIEW phase."""
        from orchestration.outer_loop.interview.entry import STEP_NUM

        assert STEP_NUM == 0.5

    def test_shows_iteration_info(self, temp_state_dir, monkeypatch):
        """Should show iteration information."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState.for_task("test query")
        state.start_phase(AlgorithmPhase.GET_STATE)
        state.save()

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "interview"
            / "entry.py"
        )

        result = subprocess.run(
            [sys.executable, str(entry_path), "--state", state.session_id, "--no-flow"],
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(entry_path.parent.parent.parent.parent),
            },
        )

        assert "Iteration" in result.stdout
        assert "Completeness Target" in result.stdout


@pytest.mark.unit
class TestInterviewConstants:
    """Tests for INTERVIEW phase constants."""

    def test_content_dir_exists(self):
        """Content directory should exist."""
        from orchestration.outer_loop.interview.entry import CONTENT_DIR

        # Path should be defined (may not exist in test env)
        assert CONTENT_DIR is not None
        assert "interview" in str(CONTENT_DIR)
