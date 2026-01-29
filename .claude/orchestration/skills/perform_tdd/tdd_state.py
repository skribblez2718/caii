"""
TDD State Management

State tracking for Test-Driven Development skill.
Implements TDDPhase enum, TDDFSM, and TDDState classes.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from orchestration.state.base import BaseFSM, BaseState

# TDD-specific sessions directory
TDD_MODULE_DIR = Path(__file__).parent
TDD_SESSIONS_DIR = TDD_MODULE_DIR / "state"

T = TypeVar("T", bound="TDDState")


class TDDPhase(Enum):
    """
    TDD workflow phases.

    Flow:
    INITIALIZED -> RED -> GREEN -> REFACTOR -> DOC -> COMPLETED
                    ^                          |
                    |_________(loop-back)______|
    """

    INITIALIZED = auto()
    RED = auto()  # Write failing test
    GREEN = auto()  # Write minimal implementation
    REFACTOR = auto()  # Improve code quality
    DOC = auto()  # Update documentation
    COMPLETED = auto()


class TDDFSM(BaseFSM):
    """
    Finite State Machine for TDD workflow.

    Enforces the RED-GREEN-REFACTOR-DOC cycle with support
    for loop-back from DOC to RED for additional features.
    """

    # Valid state transitions
    TRANSITIONS: Dict[TDDPhase, List[TDDPhase]] = {
        TDDPhase.INITIALIZED: [TDDPhase.RED],
        TDDPhase.RED: [TDDPhase.GREEN],
        TDDPhase.GREEN: [TDDPhase.REFACTOR],
        TDDPhase.REFACTOR: [TDDPhase.DOC],
        TDDPhase.DOC: [TDDPhase.COMPLETED, TDDPhase.RED],  # RED for loop-back
        TDDPhase.COMPLETED: [],  # Terminal state
    }

    def __init__(
        self,
        initial_state: TDDPhase = TDDPhase.INITIALIZED,
        cycle_count: int = 0,
    ) -> None:
        """
        Initialize TDD FSM.

        Args:
            initial_state: Starting phase (default: INITIALIZED)
            cycle_count: Current TDD cycle count
        """
        super().__init__(initial_state)
        self._cycle_count = cycle_count

    @property
    def cycle_count(self) -> int:
        """Current TDD cycle count (incremented on loop-back)."""
        return self._cycle_count

    def loop_back(self, target: TDDPhase) -> bool:
        """
        Loop back from DOC to RED for next feature cycle.

        Args:
            target: Should be TDDPhase.RED

        Returns:
            True if loop-back succeeded, False otherwise
        """
        if self._state != TDDPhase.DOC:
            return False

        if target != TDDPhase.RED:
            return False

        if self.transition(target):
            self._cycle_count += 1
            return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize FSM to dictionary."""
        base_dict = super().to_dict()
        base_dict["cycle_count"] = self._cycle_count
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TDDFSM":
        """
        Deserialize FSM from dictionary.

        Args:
            data: Dictionary with FSM state data

        Returns:
            Reconstructed TDDFSM instance
        """
        state_name = data.get("state", "INITIALIZED")
        state = TDDPhase[state_name]
        cycle_count = data.get("cycle_count", 0)

        fsm = cls(initial_state=state, cycle_count=cycle_count)

        # Restore history
        history = data.get("history", [state_name])
        fsm._history = history

        return fsm


class TDDState(BaseState):
    """
    State container for TDD skill execution.

    Tracks target file, test file, parent algorithm linkage,
    and phase outputs throughout the TDD cycle.

    Preferred instantiation:
        state = TDDState.for_algorithm("parent_id", target_file="src/foo.py")
    """

    @classmethod
    def for_algorithm(
        cls,
        algorithm_id: str,
        target_file: Optional[str] = None,
        test_file: Optional[str] = None,
    ) -> "TDDState":
        """
        Create TDD state linked to an algorithm state.

        This is the preferred way to create a TDDState instance.

        Args:
            algorithm_id: ID of the parent AlgorithmState
            target_file: Path to implementation file (optional)
            test_file: Path to test file (optional)

        Returns:
            New TDDState instance ready for execution

        Example:
            state = TDDState.for_algorithm(
                "abc123",
                target_file="src/module.py",
                test_file="tests/test_module.py"
            )
            state.save()
        """
        return cls(
            parent_algorithm_id=algorithm_id,
            target_file=target_file,
            test_file=test_file,
        )

    @classmethod
    def get_persistence_config(cls) -> Tuple[Path, str, str]:
        """
        Return TDD state persistence configuration.

        Returns:
            Tuple of (sessions_directory, file_prefix, schema_version)
        """
        return (TDD_SESSIONS_DIR, "perform-tdd", "1.0")

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        session_id: Optional[str] = None,
        parent_algorithm_id: Optional[str] = None,
        target_file: Optional[str] = None,
        test_file: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        fsm: Optional[TDDFSM] = None,
        phase_outputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize TDD state.

        Args:
            session_id: Unique session identifier (auto-generated if None)
            parent_algorithm_id: ID of parent AlgorithmState (optional)
            target_file: Path to implementation file
            test_file: Path to test file
            created_at: ISO format creation timestamp
            updated_at: ISO format update timestamp
            metadata: Arbitrary metadata dictionary
            fsm: Existing FSM to use (creates new if None)
            phase_outputs: Existing phase outputs dict
        """
        super().__init__(
            session_id=session_id,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )
        self.parent_algorithm_id = parent_algorithm_id
        self.target_file = target_file
        self.test_file = test_file
        self._fsm = fsm or TDDFSM()
        self.phase_outputs: Dict[str, Any] = phase_outputs or {}

    @property
    def current_phase(self) -> TDDPhase:
        """Current TDD phase."""
        return self._fsm.state

    @property
    def cycle_count(self) -> int:
        """Current TDD cycle count."""
        return self._fsm.cycle_count

    def advance_to_phase(self, phase: TDDPhase) -> bool:
        """
        Advance FSM to specified phase.

        Args:
            phase: Target phase

        Returns:
            True if transition succeeded
        """
        return self._fsm.transition(phase)

    def record_phase_output(self, phase: TDDPhase, output: Dict[str, Any]) -> None:
        """
        Record output for a phase.

        Args:
            phase: The phase that produced the output
            output: Output data dictionary
        """
        self.phase_outputs[phase.name] = output

    def loop_back_to_red(self) -> bool:
        """
        Loop back from DOC to RED for next feature.

        Returns:
            True if loop-back succeeded
        """
        return self._fsm.loop_back(TDDPhase.RED)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "session_id": self.session_id,
            "parent_algorithm_id": self.parent_algorithm_id,
            "target_file": self.target_file,
            "test_file": self.test_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "fsm": self._fsm.to_dict(),
            "phase_outputs": self.phase_outputs,
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Deserialize state from dictionary.

        Args:
            data: Dictionary representation of state

        Returns:
            Reconstructed TDDState instance
        """
        fsm_data = data.get("fsm", {})
        fsm = TDDFSM.from_dict(fsm_data)

        return cls(
            session_id=data.get("session_id"),
            parent_algorithm_id=data.get("parent_algorithm_id"),
            target_file=data.get("target_file"),
            test_file=data.get("test_file"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
            fsm=fsm,
            phase_outputs=data.get("phase_outputs", {}),
        )
