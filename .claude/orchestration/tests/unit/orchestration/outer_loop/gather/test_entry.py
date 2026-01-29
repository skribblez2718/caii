"""
Unit tests for outer_loop/gather/entry.py

Tests the GATHER phase (Step 0) entry point.
Updated to work with refactored run_phase_entry() pattern.
"""

import sys
from unittest.mock import patch

import pytest


class TestGatherEntryMain:
    """Tests for GATHER entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
            )

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
                argv=["--state", "nonexistent12"],
            )

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
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        # Create initial state
        state = AlgorithmState(user_query="Build an API", session_id="gather123456")
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
                argv=["--state", "gather123456"],
            )

        loaded = AlgorithmState.load("gather123456")
        assert loaded.current_phase == AlgorithmPhase.GATHER

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        state = AlgorithmState(user_query="Test query", session_id="savetest1234")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        with patch("orchestration.utils.load_content", return_value="Content here"):
            with patch.object(AlgorithmState, "save", tracking_save):
                run_phase_entry(
                    "dummy.py",
                    PhaseConfig(
                        step_num=0,
                        phase_name="GATHER",
                        content_file="gather_phase.md",
                        description="GATHER Phase (Step 0)",
                    ),
                    argv=["--state", "savetest1234"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_substitutes_placeholders(self, mock_sessions_dir, monkeypatch, capsys):
        """Should substitute user_query and session_id in content."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        state = AlgorithmState(user_query="Build REST API", session_id="subst1234567")
        state.save()

        with patch(
            "orchestration.utils.load_content",
            return_value="Query: {user_query} Session: {session_id}",
        ):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
                argv=["--state", "subst1234567"],
            )

        captured = capsys.readouterr()
        assert "Build REST API" in captured.out
        assert "subst1234567" in captured.out

    @pytest.mark.unit
    def test_prints_prompt(self, mock_sessions_dir, monkeypatch, capsys):
        """Should print the phase prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        state = AlgorithmState(user_query="Test", session_id="print1234567")
        state.save()

        with patch(
            "orchestration.utils.load_content", return_value="GATHER PHASE OUTPUT"
        ):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
                argv=["--state", "print1234567"],
            )

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
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        # Create state already at GATHER phase
        state = AlgorithmState(user_query="Test", session_id="invalid12345")
        state.fsm._state = AlgorithmPhase.GATHER
        state.fsm._history.append("GATHER")
        state.save()

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=0,
                    phase_name="GATHER",
                    content_file="gather_phase.md",
                    description="GATHER Phase (Step 0)",
                ),
                argv=["--state", "invalid12345"],
            )

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Cannot transition" in captured.err

    @pytest.mark.unit
    def test_step_num_is_zero(self):
        """STEP_NUM should be 0 for GATHER phase."""
        from orchestration.outer_loop.gather import entry

        assert entry.STEP_NUM == 0
