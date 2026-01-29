"""
perform-tdd Skill Package

Test-Driven Development skill for enforcing RED-GREEN-REFACTOR cycle.
"""

from orchestration.skills.perform_tdd.tdd_state import TDDFSM, TDDPhase, TDDState
from orchestration.skills.perform_tdd.entry import main as tdd_main
from orchestration.skills.perform_tdd.advance import main as tdd_advance
from orchestration.skills.perform_tdd.complete import main as tdd_complete

__all__ = [
    # State classes
    "TDDPhase",
    "TDDFSM",
    "TDDState",
    # Entry point functions
    "tdd_main",
    "tdd_advance",
    "tdd_complete",
]
