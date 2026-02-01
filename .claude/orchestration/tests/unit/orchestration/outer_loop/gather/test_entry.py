"""
GATHER Entry Point Unit Tests

Tests for GATHER phase entry point.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
class TestGatherEntryMain:
    """Tests for GATHER entry point main function."""

    def test_exits_without_state_arg(self):
        """Should exit with error if no --state argument."""
        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "gather"
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
            / "gather"
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

    def test_classifies_domain_for_new_state(self, temp_state_dir, monkeypatch):
        """Should classify domain if not already set."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState.for_task("implement a REST API for users")
        state.save()

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "gather"
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
        # Should have classified as CODING
        assert "CODING" in result.stdout or "coding" in result.stdout.lower()

    def test_prints_phase_header(self, temp_state_dir, monkeypatch):
        """Should print GATHER phase header."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState.for_task("test query")
        state.save()

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "gather"
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

        assert "GATHER Phase" in result.stdout

    def test_saves_state_before_output(self, temp_state_dir, monkeypatch):
        """Should save state before printing directive."""
        from orchestration.state import config as state_config

        monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState.for_task("test query")
        state.save()

        entry_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "outer_loop"
            / "gather"
            / "entry.py"
        )

        subprocess.run(
            [sys.executable, str(entry_path), "--state", state.session_id, "--no-flow"],
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(entry_path.parent.parent.parent.parent),
            },
        )

        # Reload and check state was saved
        reloaded = AlgorithmState.load(state.session_id)

        assert reloaded is not None
        # Domain should now be set
        assert reloaded.task_domain is not None

    def test_step_num_is_zero(self):
        """STEP_NUM should be 0 for GATHER phase."""
        from orchestration.outer_loop.gather.entry import STEP_NUM

        assert STEP_NUM == 0


@pytest.mark.unit
class TestGetDomainDescriptionSafe:
    """Tests for get_domain_description_safe helper."""

    def test_valid_domain(self):
        """Should return description for valid domain."""
        from orchestration.outer_loop.gather.entry import get_domain_description_safe

        desc = get_domain_description_safe("coding")

        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_invalid_domain(self):
        """Should return 'Unknown domain' for invalid domain."""
        from orchestration.outer_loop.gather.entry import get_domain_description_safe

        desc = get_domain_description_safe("invalid_domain_xyz")

        assert desc == "Unknown domain"

    def test_case_insensitive(self):
        """Should handle different cases."""
        from orchestration.outer_loop.gather.entry import get_domain_description_safe

        desc1 = get_domain_description_safe("CODING")
        desc2 = get_domain_description_safe("coding")
        desc3 = get_domain_description_safe("Coding")

        # All should work (lowercase value in enum)
        assert desc1 == desc2 == desc3
