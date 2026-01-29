"""
Agent Execution State

Provides dataclass for tracking agent execution state.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T", bound="AgentExecutionState")

# State files location
AGENT_STATE_DIR = Path(__file__).parent / "state"


@dataclass
class AgentExecutionState:
    """
    Tracks execution state for an agent.

    Attributes:
        agent_name: Name of the agent (e.g., "research")
        task_id: Unique task identifier
        current_step: Current step number (0-indexed)
        started_at: ISO timestamp when agent started
        skill_name: Name of skill that invoked this agent (if any)
        phase_id: Phase ID within the skill (if any)
        flow_id: Flow ID if part of an agent chain
        context_pattern: How to load predecessor context
        predecessors: List of predecessor agent names
        step_outputs: Dict of step number to output data
        completed_steps: List of completed step numbers
        metadata: Arbitrary metadata dictionary
    """

    agent_name: str
    task_id: str
    current_step: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    skill_name: Optional[str] = None
    phase_id: Optional[str] = None
    flow_id: Optional[str] = None
    context_pattern: str = "IMMEDIATE_PREDECESSORS"
    predecessors: List[str] = field(default_factory=list)
    step_outputs: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    completed_steps: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def state_file_path(self) -> Path:
        """Get the path to this agent's state file."""
        return AGENT_STATE_DIR / f"{self.agent_name}-{self.task_id}.json"

    def set_skill_context(
        self,
        skill_name: Optional[str] = None,
        phase_id: Optional[str] = None,
        flow_id: Optional[str] = None,
        context_pattern: str = "IMMEDIATE_PREDECESSORS",
        predecessors: Optional[List[str]] = None,
    ) -> None:
        """
        Set skill context for this agent execution.

        Args:
            skill_name: Name of invoking skill
            phase_id: Phase within the skill
            flow_id: Flow ID if part of chain
            context_pattern: How to load predecessor context
            predecessors: List of predecessor agent names
        """
        self.skill_name = skill_name
        self.phase_id = phase_id
        self.flow_id = flow_id
        self.context_pattern = context_pattern
        self.predecessors = predecessors or []

    def mark_step_complete(self, step_num: int, output: Dict[str, Any]) -> None:
        """
        Mark a step as completed.

        Args:
            step_num: Step number that completed
            output: Output data from the step
        """
        if step_num not in self.completed_steps:
            self.completed_steps.append(step_num)
        self.step_outputs[step_num] = output
        self.current_step = step_num + 1

    def is_step_completed(self, step_num: int) -> bool:
        """Check if a specific step is completed."""
        return step_num in self.completed_steps

    def get_step_output(self, step_num: int) -> Optional[Dict[str, Any]]:
        """Get the output from a specific step."""
        return self.step_outputs.get(step_num)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "skill_name": self.skill_name,
            "phase_id": self.phase_id,
            "flow_id": self.flow_id,
            "context_pattern": self.context_pattern,
            "predecessors": self.predecessors,
            "step_outputs": {str(k): v for k, v in self.step_outputs.items()},
            "completed_steps": self.completed_steps,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize state from dictionary."""
        return cls(
            agent_name=data["agent_name"],
            task_id=data["task_id"],
            current_step=data.get("current_step", 0),
            started_at=data.get("started_at", datetime.now().isoformat()),
            skill_name=data.get("skill_name"),
            phase_id=data.get("phase_id"),
            flow_id=data.get("flow_id"),
            context_pattern=data.get("context_pattern", "IMMEDIATE_PREDECESSORS"),
            predecessors=data.get("predecessors", []),
            step_outputs={int(k): v for k, v in data.get("step_outputs", {}).items()},
            completed_steps=data.get("completed_steps", []),
            metadata=data.get("metadata", {}),
        )

    def save(self) -> Path:
        """
        Save state to file.

        Returns:
            Path to the saved state file
        """
        AGENT_STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.state_file_path.write_text(json.dumps(self.to_dict(), indent=2))
        return self.state_file_path

    @classmethod
    def load(cls: Type[T], path: Path) -> Optional[T]:
        """
        Load state from file.

        Args:
            path: Path to state file

        Returns:
            AgentExecutionState instance or None if not found
        """
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return cls.from_dict(data)

    @classmethod
    def load_by_id(cls: Type[T], agent_name: str, task_id: str) -> Optional[T]:
        """
        Load state by agent name and task ID.

        Args:
            agent_name: Agent name
            task_id: Task identifier

        Returns:
            AgentExecutionState instance or None if not found
        """
        path = AGENT_STATE_DIR / f"{agent_name}-{task_id}.json"
        return cls.load(path)
