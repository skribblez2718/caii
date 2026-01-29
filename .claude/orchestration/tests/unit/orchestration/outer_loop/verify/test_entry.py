"""
Unit tests for outer_loop/verify/entry.py

Tests the VERIFY phase (Step 8) entry point.
Updated to work with refactored run_phase_entry() pattern.
"""

import sys
from unittest.mock import patch

import pytest


class TestVerifyEntryMain:
    """Tests for VERIFY entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=8,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
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
                    step_num=8,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_verify_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to VERIFY phase (step 8)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        # Create state at EXECUTE phase
        state = AlgorithmState(user_query="Build API", session_id="verify1234567")
        state.fsm._state = AlgorithmPhase.EXECUTE
        state.fsm._history.append("EXECUTE")
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    step_num=8,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
                ),
                argv=["--state", "verify1234567"],
            )

        loaded = AlgorithmState.load("verify1234567")
        assert loaded.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        state = AlgorithmState(user_query="Test", session_id="saveverify12")
        state.fsm._state = AlgorithmPhase.EXECUTE
        state.fsm._history.append("EXECUTE")
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        with patch("orchestration.utils.load_content", return_value="Content"):
            with patch.object(AlgorithmState, "save", tracking_save):
                run_phase_entry(
                    "dummy.py",
                    PhaseConfig(
                        step_num=8,
                        phase_name="VERIFY",
                        content_file="verification.md",
                        description="VERIFY Phase (Step 8)",
                    ),
                    argv=["--state", "saveverify12"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_eight(self):
        """STEP_NUM should be 8 for VERIFY phase."""
        from orchestration.outer_loop.verify import entry

        assert entry.STEP_NUM == 8
