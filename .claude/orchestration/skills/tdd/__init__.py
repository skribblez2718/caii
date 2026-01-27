"""
TDD Skill Package

Test-Driven Development skill for enforcing RED-GREEN-REFACTOR cycle.
"""

from orchestration.skills.tdd.tdd_state import TDDFSM, TDDPhase, TDDState
from orchestration.skills.tdd.entry import main as tdd_main
from orchestration.skills.tdd.advance import main as tdd_advance
from orchestration.skills.tdd.complete import main as tdd_complete

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
