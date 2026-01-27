"""
TDD Entry Point Tests

Tests for entry.py, advance.py, and complete.py.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestTDDEntryModule:
    """Tests for TDD entry point module."""

    def test_entry_module_exists(self):
        """Entry module should be importable."""
        from orchestration.skills.tdd import entry

        assert hasattr(entry, "main")

    def test_entry_creates_new_state_when_no_tdd_state_arg(
        self, temp_state_dir, monkeypatch, capsys
    ):
        """Entry should create new TDDState when --tdd-state not provided."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import entry as entry_module
        from orchestration.skills.tdd.tdd_state import TDDPhase

        with patch.object(sys, "argv", ["entry.py", "--algorithm-state", "alg123"]):
            entry_module.main()

        captured = capsys.readouterr()

        # Should output phase content for RED
        assert "RED" in captured.out or "test" in captured.out.lower()

        # Should have created a state file
        state_files = list(temp_state_dir.glob("tdd-*.json"))
        assert len(state_files) == 1

    def test_entry_loads_existing_state(self, temp_state_dir, monkeypatch, capsys):
        """Entry should load existing TDDState when --tdd-state provided."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import entry as entry_module
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        # Create existing state at GREEN
        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.save()

        with patch.object(
            sys,
            "argv",
            [
                "entry.py",
                "--algorithm-state",
                "alg123",
                "--tdd-state",
                state.session_id,
            ],
        ):
            entry_module.main()

        captured = capsys.readouterr()

        # Should output phase content for GREEN (current phase)
        assert "GREEN" in captured.out or "implementation" in captured.out.lower()

    def test_entry_accepts_target_and_test_file_args(
        self, temp_state_dir, monkeypatch, capsys
    ):
        """Entry should accept --target and --test arguments."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import entry as entry_module
        from orchestration.skills.tdd.tdd_state import TDDState

        with patch.object(
            sys,
            "argv",
            [
                "entry.py",
                "--algorithm-state",
                "alg123",
                "--target",
                "src/foo.py",
                "--test",
                "tests/test_foo.py",
            ],
        ):
            entry_module.main()

        # Load the created state and verify
        state_files = list(temp_state_dir.glob("tdd-*.json"))
        assert len(state_files) == 1

        import json

        state_data = json.loads(state_files[0].read_text())
        assert state_data["target_file"] == "src/foo.py"
        assert state_data["test_file"] == "tests/test_foo.py"


@pytest.mark.unit
class TestTDDAdvanceModule:
    """Tests for TDD advance module."""

    def test_advance_module_exists(self):
        """Advance module should be importable."""
        from orchestration.skills.tdd import advance

        assert hasattr(advance, "main")

    def test_advance_transitions_to_next_phase(
        self, temp_state_dir, monkeypatch, capsys
    ):
        """Advance should transition to next phase."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import advance as advance_module
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        # Create state at RED
        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.save()

        with patch.object(sys, "argv", ["advance.py", "--tdd-state", state.session_id]):
            advance_module.main()

        # Reload and verify
        reloaded = TDDState.load(state.session_id)
        assert reloaded.current_phase == TDDPhase.GREEN

    def test_advance_with_phase_output(self, temp_state_dir, monkeypatch, capsys):
        """Advance should record phase output if provided."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import advance as advance_module
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.save()

        with patch.object(
            sys,
            "argv",
            [
                "advance.py",
                "--tdd-state",
                state.session_id,
                "--output",
                '{"test_file": "test_foo.py"}',
            ],
        ):
            advance_module.main()

        reloaded = TDDState.load(state.session_id)
        assert reloaded.phase_outputs.get("RED") == {"test_file": "test_foo.py"}


@pytest.mark.unit
class TestTDDCompleteModule:
    """Tests for TDD complete module."""

    def test_complete_module_exists(self):
        """Complete module should be importable."""
        from orchestration.skills.tdd import complete

        assert hasattr(complete, "main")

    def test_complete_marks_session_completed(
        self, temp_state_dir, monkeypatch, capsys
    ):
        """Complete should transition to COMPLETED state."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import complete as complete_module
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        # Create state at DOC (ready for completion)
        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)
        state.save()

        with patch.object(
            sys, "argv", ["complete.py", "--tdd-state", state.session_id]
        ):
            complete_module.main()

        reloaded = TDDState.load(state.session_id)
        assert reloaded.current_phase == TDDPhase.COMPLETED

    def test_complete_supports_loop_back(self, temp_state_dir, monkeypatch, capsys):
        """Complete with --loop-back should restart cycle."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd import complete as complete_module
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)
        state.save()

        with patch.object(
            sys, "argv", ["complete.py", "--tdd-state", state.session_id, "--loop-back"]
        ):
            complete_module.main()

        reloaded = TDDState.load(state.session_id)
        assert reloaded.current_phase == TDDPhase.RED
        assert reloaded.cycle_count == 1
