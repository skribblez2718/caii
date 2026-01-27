"""
TDD FSM Transition Tests

Dedicated tests for FSM transition validation.
"""

import pytest


@pytest.mark.unit
@pytest.mark.fsm
class TestTDDFSMTransitions:
    """Test all valid and invalid transitions."""

    def test_transitions_from_initialized(self):
        """INITIALIZED should only allow RED transition."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()

        # Valid
        assert fsm.can_transition(TDDPhase.RED)

        # Invalid
        assert not fsm.can_transition(TDDPhase.GREEN)
        assert not fsm.can_transition(TDDPhase.REFACTOR)
        assert not fsm.can_transition(TDDPhase.DOC)
        assert not fsm.can_transition(TDDPhase.COMPLETED)

    def test_transitions_from_red(self):
        """RED should only allow GREEN transition."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)

        # Valid
        assert fsm.can_transition(TDDPhase.GREEN)

        # Invalid
        assert not fsm.can_transition(TDDPhase.RED)
        assert not fsm.can_transition(TDDPhase.REFACTOR)
        assert not fsm.can_transition(TDDPhase.DOC)
        assert not fsm.can_transition(TDDPhase.COMPLETED)

    def test_transitions_from_green(self):
        """GREEN should only allow REFACTOR transition."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)

        # Valid
        assert fsm.can_transition(TDDPhase.REFACTOR)

        # Invalid
        assert not fsm.can_transition(TDDPhase.RED)
        assert not fsm.can_transition(TDDPhase.GREEN)
        assert not fsm.can_transition(TDDPhase.DOC)
        assert not fsm.can_transition(TDDPhase.COMPLETED)

    def test_transitions_from_refactor(self):
        """REFACTOR should only allow DOC transition."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)

        # Valid
        assert fsm.can_transition(TDDPhase.DOC)

        # Invalid
        assert not fsm.can_transition(TDDPhase.RED)
        assert not fsm.can_transition(TDDPhase.GREEN)
        assert not fsm.can_transition(TDDPhase.REFACTOR)
        assert not fsm.can_transition(TDDPhase.COMPLETED)

    def test_transitions_from_doc(self):
        """DOC should allow COMPLETED or RED (loop-back)."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)

        # Valid
        assert fsm.can_transition(TDDPhase.COMPLETED)
        assert fsm.can_transition(TDDPhase.RED)  # Loop-back

        # Invalid
        assert not fsm.can_transition(TDDPhase.GREEN)
        assert not fsm.can_transition(TDDPhase.REFACTOR)
        assert not fsm.can_transition(TDDPhase.DOC)

    def test_transitions_from_completed(self):
        """COMPLETED should be terminal (no transitions)."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.transition(TDDPhase.COMPLETED)

        # All invalid
        for phase in TDDPhase:
            assert not fsm.can_transition(phase)


@pytest.mark.unit
@pytest.mark.fsm
class TestTDDFSMLoopBack:
    """Test loop-back functionality."""

    def test_loop_back_only_valid_from_doc(self):
        """loop_back should only work from DOC phase."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        phases_to_try = [
            TDDPhase.INITIALIZED,
            TDDPhase.RED,
            TDDPhase.GREEN,
            TDDPhase.REFACTOR,
            TDDPhase.COMPLETED,
        ]

        for start_phase in phases_to_try:
            fsm = TDDFSM(initial_state=start_phase)
            assert not fsm.loop_back(
                TDDPhase.RED
            ), f"loop_back worked from {start_phase}"

    def test_loop_back_from_doc_succeeds(self):
        """loop_back from DOC to RED should succeed."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM(initial_state=TDDPhase.DOC)

        result = fsm.loop_back(TDDPhase.RED)

        assert result is True
        assert fsm.state == TDDPhase.RED

    def test_loop_back_increments_on_each_cycle(self):
        """Each loop-back should increment cycle count."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        assert fsm.cycle_count == 0

        # First cycle
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.loop_back(TDDPhase.RED)
        assert fsm.cycle_count == 1

        # Second cycle
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.loop_back(TDDPhase.RED)
        assert fsm.cycle_count == 2

        # Third cycle
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.loop_back(TDDPhase.RED)
        assert fsm.cycle_count == 3

    def test_loop_back_records_in_history(self):
        """Loop-back should be recorded in history."""
        from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase

        fsm = TDDFSM()
        fsm.transition(TDDPhase.RED)
        fsm.transition(TDDPhase.GREEN)
        fsm.transition(TDDPhase.REFACTOR)
        fsm.transition(TDDPhase.DOC)
        fsm.loop_back(TDDPhase.RED)

        expected = ["INITIALIZED", "RED", "GREEN", "REFACTOR", "DOC", "RED"]
        assert fsm.history == expected
