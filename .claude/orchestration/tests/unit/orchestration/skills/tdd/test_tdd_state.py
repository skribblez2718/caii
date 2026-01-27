"""
TDD State Unit Tests

Tests for TDDPhase, TDDFSM, and TDDState classes.
Following RED-GREEN-REFACTOR: Write tests FIRST.
"""

import json
from pathlib import Path

import pytest

# ==============================================================================
# TDDPhase Enum Tests
# ==============================================================================


@pytest.mark.unit
class TestTDDPhase:
    """Tests for TDDPhase enum."""

    def test_phase_values_exist(self):
        """TDDPhase should have all required phases."""
        from orchestration.skills.tdd.tdd_state import TDDPhase

        assert hasattr(TDDPhase, "INITIALIZED")
        assert hasattr(TDDPhase, "RED")
        assert hasattr(TDDPhase, "GREEN")
        assert hasattr(TDDPhase, "REFACTOR")
        assert hasattr(TDDPhase, "DOC")
        assert hasattr(TDDPhase, "COMPLETED")

    def test_phase_ordering(self):
        """Phases should be in expected order."""
        from orchestration.skills.tdd.tdd_state import TDDPhase

        phases = list(TDDPhase)
        phase_names = [p.name for p in phases]

        assert phase_names.index("INITIALIZED") < phase_names.index("RED")
        assert phase_names.index("RED") < phase_names.index("GREEN")
        assert phase_names.index("GREEN") < phase_names.index("REFACTOR")
        assert phase_names.index("REFACTOR") < phase_names.index("DOC")
        assert phase_names.index("DOC") < phase_names.index("COMPLETED")


# ==============================================================================
# TDDFSM Tests
# ==============================================================================


@pytest.mark.unit
@pytest.mark.fsm
class TestTDDFSM:
    """Tests for TDD finite state machine."""

    def test_initial_state_is_initialized(self):
        """FSM should start in INITIALIZED state."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()

        assert fsm.state == TDDPhase.INITIALIZED

    def test_valid_transition_initialized_to_red(self):
        """FSM should allow INITIALIZED -> RED transition."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()

        assert fsm.transition(TDDPhase.RED)
        assert fsm.state == TDDPhase.RED

    def test_valid_forward_transitions(self):
        """FSM should allow full forward path."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()

        assert fsm.transition(TDDPhase.RED)
        assert fsm.transition(TDDPhase.GREEN)
        assert fsm.transition(TDDPhase.REFACTOR)
        assert fsm.transition(TDDPhase.DOC)
        assert fsm.transition(TDDPhase.COMPLETED)
        assert fsm.state == TDDPhase.COMPLETED

    def test_invalid_transition_skip_green(self):
        """FSM should reject skipping GREEN phase."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)

        assert not fsm.transition(TDDPhase.REFACTOR)
        assert fsm.state == TDDPhase.RED

    def test_invalid_transition_skip_to_doc(self):
        """FSM should reject skipping to DOC from RED."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)

        assert not fsm.transition(TDDPhase.DOC)
        assert fsm.state == TDDPhase.RED

    def test_loopback_from_doc_to_red(self):
        """FSM should allow DOC -> RED for next feature cycle."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)

        assert fsm.loop_back(TDDPhase.RED)
        assert fsm.state == TDDPhase.RED

    def test_loopback_increments_cycle_count(self):
        """Loop-back should increment cycle counter."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        assert fsm.cycle_count == 0

        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.loop_back(TDDPhase.RED)

        assert fsm.cycle_count == 1

    def test_loopback_only_from_doc(self):
        """Loop-back should only work from DOC phase."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)

        assert not fsm.loop_back(TDDPhase.RED)
        assert fsm.state == TDDPhase.GREEN

    def test_history_tracking(self):
        """FSM should track state history."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)

        assert fsm.history == ["INITIALIZED", "RED", "GREEN"]

    def test_serialization_round_trip(self):
        """FSM should serialize and deserialize correctly."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)

        data = fsm.to_dict()
        restored = TDDFSM.from_dict(data)

        assert restored.state == fsm.state
        assert restored.history == fsm.history
        assert restored.cycle_count == fsm.cycle_count

    def test_completed_is_terminal(self):
        """COMPLETED should be a terminal state."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.transition(TDDPhase.COMPLETED)

        # Should not allow any further transitions
        assert not fsm.transition(TDDPhase.RED)
        assert fsm.state == TDDPhase.COMPLETED


# ==============================================================================
# TDDState Factory Method Tests
# ==============================================================================


@pytest.mark.unit
class TestTDDStateForAlgorithm:
    """Tests for TDDState.for_algorithm() factory method."""

    def test_for_algorithm_creates_state_with_parent_id(self):
        """for_algorithm should create state linked to parent algorithm."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState.for_algorithm("parent123456")

        assert state.parent_algorithm_id == "parent123456"

    def test_for_algorithm_accepts_target_file(self):
        """for_algorithm should accept target_file parameter."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState.for_algorithm("parent", target_file="src/module.py")

        assert state.target_file == "src/module.py"

    def test_for_algorithm_accepts_test_file(self):
        """for_algorithm should accept test_file parameter."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState.for_algorithm("parent", test_file="tests/test_module.py")

        assert state.test_file == "tests/test_module.py"

    def test_for_algorithm_defaults_files_to_none(self):
        """for_algorithm should default files to None."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState.for_algorithm("parent")

        assert state.target_file is None
        assert state.test_file is None

    def test_for_algorithm_creates_fsm_at_initialized(self):
        """for_algorithm should create FSM at INITIALIZED phase."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState.for_algorithm("parent")

        assert state.current_phase == TDDPhase.INITIALIZED

    def test_for_algorithm_creates_valid_session_id(self):
        """for_algorithm should create valid 12-char session_id."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState.for_algorithm("parent")

        assert len(state.session_id) == 12

    def test_for_algorithm_can_save_and_load(self, temp_state_dir, monkeypatch):
        """State created with for_algorithm should save and load correctly."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd.tdd_state import TDDState

        original = TDDState.for_algorithm(
            "parent123", target_file="src/foo.py", test_file="tests/test_foo.py"
        )
        original.save()

        loaded = TDDState.load(original.session_id)

        assert loaded is not None
        assert loaded.parent_algorithm_id == "parent123"
        assert loaded.target_file == "src/foo.py"
        assert loaded.test_file == "tests/test_foo.py"


# ==============================================================================
# TDDState Tests
# ==============================================================================


@pytest.mark.unit
class TestTDDState:
    """Tests for TDDState class."""

    def test_state_creation_generates_session_id(self):
        """State should auto-generate session ID."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState()

        assert state.session_id is not None
        assert len(state.session_id) == 12

    def test_state_creation_with_explicit_session_id(self):
        """State should accept explicit session ID."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState(session_id="test12345678")

        assert state.session_id == "test12345678"

    def test_state_creation_with_parent_algorithm_id(self):
        """State should link to parent algorithm state."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState(parent_algorithm_id="parent123456")

        assert state.parent_algorithm_id == "parent123456"

    def test_state_tracks_target_file(self):
        """State should track target implementation file."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState(target_file="src/module.py")

        assert state.target_file == "src/module.py"

    def test_state_tracks_test_file(self):
        """State should track test file."""
        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState(test_file="tests/test_module.py")

        assert state.test_file == "tests/test_module.py"

    def test_current_phase_property(self):
        """State should expose current phase via property."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()

        assert state.current_phase == TDDPhase.INITIALIZED

    def test_advance_to_phase(self):
        """State should advance FSM via advance_to_phase."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        result = state.advance_to_phase(TDDPhase.RED)

        assert result is True
        assert state.current_phase == TDDPhase.RED

    def test_phase_outputs_storage(self):
        """State should store phase outputs."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.record_phase_output(TDDPhase.RED, {"test_file": "test_foo.py"})

        assert state.phase_outputs.get("RED") == {"test_file": "test_foo.py"}

    def test_serialization_round_trip(self, temp_state_dir, monkeypatch):
        """State should serialize and deserialize correctly."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        original = TDDState(
            target_file="src/foo.py",
            test_file="tests/test_foo.py",
            parent_algorithm_id="parent123",
        )
        original.advance_to_phase(TDDPhase.RED)
        original.record_phase_output(TDDPhase.RED, {"created": True})
        original.save()

        loaded = TDDState.load(original.session_id)

        assert loaded is not None
        assert loaded.session_id == original.session_id
        assert loaded.target_file == original.target_file
        assert loaded.test_file == original.test_file
        assert loaded.parent_algorithm_id == original.parent_algorithm_id
        assert loaded.current_phase == TDDPhase.RED
        assert loaded.phase_outputs == original.phase_outputs

    def test_cycle_count_property(self):
        """State should expose cycle count from FSM."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)
        state.loop_back_to_red()

        assert state.cycle_count == 1

    def test_loop_back_method(self):
        """State should have loop_back_to_red helper."""
        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)

        result = state.loop_back_to_red()

        assert result is True
        assert state.current_phase == TDDPhase.RED

    def test_file_prefix_for_tdd_sessions(self, temp_state_dir, monkeypatch):
        """TDD state files should use tdd- prefix."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd.tdd_state import TDDState

        state = TDDState()
        state.save()

        expected_file = temp_state_dir / f"tdd-{state.session_id}.json"
        assert expected_file.exists()


# ==============================================================================
# Integration-style Tests (but still unit scope)
# ==============================================================================


@pytest.mark.unit
class TestTDDStateCycleFlow:
    """Test complete TDD cycle flow through state management."""

    def test_complete_single_cycle(self, temp_state_dir, monkeypatch):
        """State should support complete single TDD cycle."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState(target_file="src/foo.py", test_file="tests/test_foo.py")

        # RED
        assert state.advance_to_phase(TDDPhase.RED)
        state.record_phase_output(TDDPhase.RED, {"test_written": True})
        state.save()

        # GREEN
        assert state.advance_to_phase(TDDPhase.GREEN)
        state.record_phase_output(TDDPhase.GREEN, {"implementation_written": True})
        state.save()

        # REFACTOR
        assert state.advance_to_phase(TDDPhase.REFACTOR)
        state.record_phase_output(TDDPhase.REFACTOR, {"refactored": True})
        state.save()

        # DOC
        assert state.advance_to_phase(TDDPhase.DOC)
        state.record_phase_output(TDDPhase.DOC, {"docs_updated": True})
        state.save()

        # COMPLETED
        assert state.advance_to_phase(TDDPhase.COMPLETED)
        state.save()

        assert state.current_phase == TDDPhase.COMPLETED
        assert len(state.phase_outputs) == 4

    def test_multiple_cycles(self, temp_state_dir, monkeypatch):
        """State should support multiple RED-GREEN-REFACTOR-DOC cycles."""
        from orchestration.skills.tdd import tdd_state as tdd_module

        monkeypatch.setattr(tdd_module, "TDD_SESSIONS_DIR", temp_state_dir)

        from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState

        state = TDDState()

        # First cycle
        state.advance_to_phase(TDDPhase.RED)
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)
        state.loop_back_to_red()

        assert state.cycle_count == 1
        assert state.current_phase == TDDPhase.RED

        # Second cycle
        state.advance_to_phase(TDDPhase.GREEN)
        state.advance_to_phase(TDDPhase.REFACTOR)
        state.advance_to_phase(TDDPhase.DOC)
        state.loop_back_to_red()

        assert state.cycle_count == 2
        assert state.current_phase == TDDPhase.RED
