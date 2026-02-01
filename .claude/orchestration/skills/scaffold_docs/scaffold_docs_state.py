"""
Scaffold-Docs State Management

State tracking for scaffold-docs skill.
Implements ScaffoldDocsPhase enum, ScaffoldDocsFSM, and ScaffoldDocsState classes.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, TypeVar

from orchestration.state.base import BaseFSM, BaseState

# Scaffold-docs specific sessions directory
MODULE_DIR = Path(__file__).parent
SESSIONS_DIR = MODULE_DIR / "state"

T = TypeVar("T", bound="ScaffoldDocsState")


class ScaffoldDocsPhase(Enum):
    """
    Scaffold-docs workflow phases.

    Scaffold Flow:
    INITIALIZED -> CLARIFICATION -> ANALYSIS -> SYNTHESIS -> VALIDATION -> COMPLETED

    Update Flow:
    INITIALIZED -> ANALYSIS -> SYNTHESIS -> VALIDATION -> COMPLETED
    """

    INITIALIZED = auto()
    CLARIFICATION = auto()  # Scaffold mode only
    ANALYSIS = auto()
    SYNTHESIS = auto()
    VALIDATION = auto()
    COMPLETED = auto()


class ScaffoldDocsFSM(BaseFSM):
    """
    Finite State Machine for scaffold-docs workflow.

    Supports two modes:
    - scaffold: Full flow with clarification phase
    - update: Skip clarification, start at analysis
    """

    # Valid state transitions for scaffold mode
    SCAFFOLD_TRANSITIONS: Dict[ScaffoldDocsPhase, List[ScaffoldDocsPhase]] = {
        ScaffoldDocsPhase.INITIALIZED: [ScaffoldDocsPhase.CLARIFICATION],
        ScaffoldDocsPhase.CLARIFICATION: [ScaffoldDocsPhase.ANALYSIS],
        ScaffoldDocsPhase.ANALYSIS: [ScaffoldDocsPhase.SYNTHESIS],
        ScaffoldDocsPhase.SYNTHESIS: [ScaffoldDocsPhase.VALIDATION],
        ScaffoldDocsPhase.VALIDATION: [ScaffoldDocsPhase.COMPLETED],
        ScaffoldDocsPhase.COMPLETED: [],  # Terminal state
    }

    # Valid state transitions for update mode
    UPDATE_TRANSITIONS: Dict[ScaffoldDocsPhase, List[ScaffoldDocsPhase]] = {
        ScaffoldDocsPhase.INITIALIZED: [ScaffoldDocsPhase.ANALYSIS],
        ScaffoldDocsPhase.ANALYSIS: [ScaffoldDocsPhase.SYNTHESIS],
        ScaffoldDocsPhase.SYNTHESIS: [ScaffoldDocsPhase.VALIDATION],
        ScaffoldDocsPhase.VALIDATION: [ScaffoldDocsPhase.COMPLETED],
        ScaffoldDocsPhase.COMPLETED: [],  # Terminal state
    }

    def __init__(
        self,
        initial_state: ScaffoldDocsPhase = ScaffoldDocsPhase.INITIALIZED,
        mode: Literal["scaffold", "update"] = "scaffold",
    ) -> None:
        """
        Initialize scaffold-docs FSM.

        Args:
            initial_state: Starting phase (default: INITIALIZED)
            mode: Operation mode ('scaffold' or 'update')
        """
        super().__init__(initial_state)
        self._mode = mode

    @property
    def mode(self) -> Literal["scaffold", "update"]:
        """Current operation mode."""
        return self._mode

    @property
    def TRANSITIONS(  # noqa: N802 pylint: disable=invalid-name
        self,
    ) -> Dict[ScaffoldDocsPhase, List[ScaffoldDocsPhase]]:
        """Get transitions for current mode."""
        if self._mode == "update":
            return self.UPDATE_TRANSITIONS
        return self.SCAFFOLD_TRANSITIONS

    def to_dict(self) -> Dict[str, Any]:
        """Serialize FSM to dictionary."""
        base_dict = super().to_dict()
        base_dict["mode"] = self._mode
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScaffoldDocsFSM":
        """
        Deserialize FSM from dictionary.

        Args:
            data: Dictionary with FSM state data

        Returns:
            Reconstructed ScaffoldDocsFSM instance
        """
        state_name = data.get("state", "INITIALIZED")
        state = ScaffoldDocsPhase[state_name]
        mode = data.get("mode", "scaffold")

        fsm = cls(initial_state=state, mode=mode)

        # Restore history
        history = data.get("history", [state_name])
        fsm._history = history

        return fsm


class ScaffoldDocsState(BaseState):
    """
    State container for scaffold-docs skill execution.

    Tracks target path, detected language, project configuration,
    and created/updated files throughout the workflow.

    Preferred instantiation:
        state = ScaffoldDocsState.for_algorithm("parent_id", target_path="/path/to/project")
    """

    @classmethod
    def for_algorithm(
        cls,
        algorithm_id: str,
        target_path: Optional[str] = None,
        mode: Literal["scaffold", "update"] = "scaffold",
    ) -> "ScaffoldDocsState":
        """
        Create scaffold-docs state linked to an algorithm state.

        This is the preferred way to create a ScaffoldDocsState instance.

        Args:
            algorithm_id: ID of the parent AlgorithmState
            target_path: Path to target project directory
            mode: Operation mode ('scaffold' or 'update')

        Returns:
            New ScaffoldDocsState instance ready for execution

        Example:
            state = ScaffoldDocsState.for_algorithm(
                "abc123",
                target_path="/home/user/projects/my-app",
                mode="scaffold"
            )
            state.save()
        """
        return cls(
            parent_algorithm_id=algorithm_id,
            target_path=target_path,
            mode=mode,
        )

    @classmethod
    def get_persistence_config(cls) -> Tuple[Path, str, str]:
        """
        Return scaffold-docs state persistence configuration.

        Returns:
            Tuple of (sessions_directory, file_prefix, schema_version)
        """
        return (SESSIONS_DIR, "scaffold-docs", "1.0")

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        session_id: Optional[str] = None,
        parent_algorithm_id: Optional[str] = None,
        target_path: Optional[str] = None,
        mode: Literal["scaffold", "update"] = "scaffold",
        detected_language: Optional[str] = None,
        project_config: Optional[Dict[str, Any]] = None,
        created_files: Optional[List[str]] = None,
        updated_files: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        fsm: Optional[ScaffoldDocsFSM] = None,
        phase_outputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize scaffold-docs state.

        Args:
            session_id: Unique session identifier (auto-generated if None)
            parent_algorithm_id: ID of parent AlgorithmState (optional)
            target_path: Path to target project directory
            mode: Operation mode ('scaffold' or 'update')
            detected_language: Detected project language
            project_config: User answers from clarification phase
            created_files: List of files created during execution
            updated_files: List of files updated during execution
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
        self.target_path = target_path
        self.mode: Literal["scaffold", "update"] = mode
        self.detected_language = detected_language
        self.project_config: Dict[str, Any] = project_config or {}
        self.created_files: List[str] = created_files or []
        self.updated_files: List[str] = updated_files or []
        self._fsm = fsm or ScaffoldDocsFSM(mode=mode)
        self.phase_outputs: Dict[str, Any] = phase_outputs or {}

    @property
    def current_phase(self) -> ScaffoldDocsPhase:
        """Current scaffold-docs phase."""
        return self._fsm.state

    def advance_to_phase(self, phase: ScaffoldDocsPhase) -> bool:
        """
        Advance FSM to specified phase.

        Args:
            phase: Target phase

        Returns:
            True if transition succeeded
        """
        return self._fsm.transition(phase)

    def record_phase_output(
        self, phase: ScaffoldDocsPhase, output: Dict[str, Any]
    ) -> None:
        """
        Record output for a phase.

        Args:
            phase: The phase that produced the output
            output: Output data dictionary
        """
        self.phase_outputs[phase.name] = output

    def add_created_file(self, file_path: str) -> None:
        """
        Record a created file.

        Args:
            file_path: Path to the created file
        """
        if file_path not in self.created_files:
            self.created_files.append(file_path)

    def add_updated_file(self, file_path: str) -> None:
        """
        Record an updated file.

        Args:
            file_path: Path to the updated file
        """
        if file_path not in self.updated_files:
            self.updated_files.append(file_path)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "session_id": self.session_id,
            "parent_algorithm_id": self.parent_algorithm_id,
            "target_path": self.target_path,
            "mode": self.mode,
            "detected_language": self.detected_language,
            "project_config": self.project_config,
            "created_files": self.created_files,
            "updated_files": self.updated_files,
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
            Reconstructed ScaffoldDocsState instance
        """
        fsm_data = data.get("fsm", {})
        fsm = ScaffoldDocsFSM.from_dict(fsm_data)

        return cls(
            session_id=data.get("session_id"),
            parent_algorithm_id=data.get("parent_algorithm_id"),
            target_path=data.get("target_path"),
            mode=data.get("mode", "scaffold"),
            detected_language=data.get("detected_language"),
            project_config=data.get("project_config", {}),
            created_files=data.get("created_files", []),
            updated_files=data.get("updated_files", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
            fsm=fsm,
            phase_outputs=data.get("phase_outputs", {}),
        )
