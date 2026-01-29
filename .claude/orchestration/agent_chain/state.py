"""
Chain State Management

Tracks the execution state of an agent chain.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T", bound="ChainState")

# State files location
CHAIN_STATE_DIR = Path(__file__).parent.parent / "agent_chain" / "state"


@dataclass
class ChainState:
    """
    Tracks execution state of an agent chain.

    Attributes:
        task_id: Unique identifier for this task/chain execution
        flow_id: Identifier of the flow being executed
        skill_name: Name of the skill that owns this flow (if applicable)
        phase_id: Phase within the skill (if applicable)
        current_step_index: Index of current step in the flow
        completed_agents: List of agent names that have completed
        memory_files_created: Dict mapping agent names to their memory file paths
        started_at: ISO timestamp when chain started
        metadata: Arbitrary metadata dictionary
        learnings_injected_for: List of agents that have received learnings directive
    """

    task_id: str
    flow_id: str
    skill_name: Optional[str] = None
    phase_id: Optional[str] = None
    current_step_index: int = 0
    completed_agents: List[str] = field(default_factory=list)
    memory_files_created: Dict[str, str] = field(default_factory=dict)
    learnings_injected_for: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_agent_complete(self, agent_name: str, memory_file_path: str) -> None:
        """
        Mark an agent as completed.

        Args:
            agent_name: Name of the agent that completed
            memory_file_path: Path to the memory file the agent created
        """
        if agent_name not in self.completed_agents:
            self.completed_agents.append(agent_name)
        self.memory_files_created[agent_name] = memory_file_path

    def advance_step(self) -> None:
        """Advance to the next step in the flow."""
        self.current_step_index += 1

    def is_agent_completed(self, agent_name: str) -> bool:
        """Check if an agent has completed."""
        return agent_name in self.completed_agents

    def get_memory_file(self, agent_name: str) -> Optional[str]:
        """Get the memory file path for a completed agent."""
        return self.memory_files_created.get(agent_name)

    def needs_learnings_directive(self, agent_name: str) -> bool:
        """
        Check if this agent needs learnings directive injected.

        Args:
            agent_name: Name of the agent to check

        Returns:
            True if learnings directive has not yet been injected for this agent
        """
        return agent_name not in self.learnings_injected_for

    def mark_learnings_injected(self, agent_name: str) -> None:
        """
        Mark that learnings directive was injected for this agent.

        Args:
            agent_name: Name of the agent that received the directive
        """
        if agent_name not in self.learnings_injected_for:
            self.learnings_injected_for.append(agent_name)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "task_id": self.task_id,
            "flow_id": self.flow_id,
            "skill_name": self.skill_name,
            "phase_id": self.phase_id,
            "current_step_index": self.current_step_index,
            "completed_agents": self.completed_agents,
            "memory_files_created": self.memory_files_created,
            "learnings_injected_for": self.learnings_injected_for,
            "started_at": self.started_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize state from dictionary."""
        return cls(
            task_id=data["task_id"],
            flow_id=data["flow_id"],
            skill_name=data.get("skill_name"),
            phase_id=data.get("phase_id"),
            current_step_index=data.get("current_step_index", 0),
            completed_agents=data.get("completed_agents", []),
            memory_files_created=data.get("memory_files_created", {}),
            learnings_injected_for=data.get("learnings_injected_for", []),
            started_at=data.get("started_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )

    def save(self) -> Path:
        """
        Save state to file.

        Returns:
            Path to the saved state file
        """
        CHAIN_STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file = CHAIN_STATE_DIR / f"chain-{self.task_id}.json"
        state_file.write_text(json.dumps(self.to_dict(), indent=2))
        return state_file

    @classmethod
    def load(cls: Type[T], task_id: str) -> Optional[T]:
        """
        Load state from file.

        Args:
            task_id: Task ID to load

        Returns:
            ChainState instance or None if not found
        """
        state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
        if not state_file.exists():
            return None
        data = json.loads(state_file.read_text())
        return cls.from_dict(data)

    @classmethod
    def load_from_path(cls: Type[T], path: Path) -> Optional[T]:
        """
        Load state from a specific file path.

        Args:
            path: Path to state file

        Returns:
            ChainState instance or None if not found
        """
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return cls.from_dict(data)
