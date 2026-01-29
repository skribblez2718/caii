"""
Agent Flow Definitions

Provides dataclasses for defining agent execution flows.
Flows define sequences of agents and how context passes between them.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ContextPattern(Enum):
    """How an agent loads context from predecessors."""

    WORKFLOW_ONLY = "workflow_only"
    """Load only workflow-level context (no predecessor memory files)."""

    IMMEDIATE_PREDECESSORS = "immediate_predecessors"
    """Load context from immediate predecessor agents only."""

    MULTIPLE_PREDECESSORS = "multiple_predecessors"
    """Load context from multiple specified predecessor agents."""


@dataclass(frozen=True)
class FlowStep:
    """
    A single step in an agent flow.

    Defines which agent to invoke and how it receives context.

    Attributes:
        agent_name: Name of the agent (e.g., "clarification", "research")
        context_pattern: How to load predecessor context
        predecessors: Tuple of agent names to load context from
        content_file: Path to agent-specific content file (relative to skill content dir)
        conditional: If True, step may be skipped based on runtime conditions
    """

    agent_name: str
    context_pattern: ContextPattern
    predecessors: Tuple[str, ...] = ()
    content_file: Optional[str] = None
    conditional: bool = False

    def __post_init__(self) -> None:
        """Validate FlowStep configuration."""
        if self.context_pattern == ContextPattern.WORKFLOW_ONLY and self.predecessors:
            raise ValueError(
                f"FlowStep for {self.agent_name}: WORKFLOW_ONLY pattern "
                "should not have predecessors"
            )

        if self.context_pattern == ContextPattern.IMMEDIATE_PREDECESSORS:
            if len(self.predecessors) > 1:
                raise ValueError(
                    f"FlowStep for {self.agent_name}: IMMEDIATE_PREDECESSORS "
                    "should have at most one predecessor"
                )

        if self.context_pattern == ContextPattern.MULTIPLE_PREDECESSORS:
            if len(self.predecessors) < 2:
                raise ValueError(
                    f"FlowStep for {self.agent_name}: MULTIPLE_PREDECESSORS "
                    "should have at least two predecessors"
                )


@dataclass(frozen=True)
class AgentFlow:
    """
    A complete agent flow defining a sequence of agent invocations.

    Attributes:
        flow_id: Unique identifier for this flow (e.g., "perform-tdd-red")
        name: Human-readable name (e.g., "TDD RED Phase")
        steps: Tuple of FlowStep objects defining the sequence
        source: Where this flow is defined ("skill" or "dynamic")
    """

    flow_id: str
    name: str
    steps: Tuple[FlowStep, ...]
    source: str = "skill"

    def __post_init__(self) -> None:
        """Validate AgentFlow configuration."""
        if not self.steps:
            raise ValueError(f"AgentFlow {self.flow_id} must have at least one step")

        if self.source not in ("skill", "dynamic"):
            raise ValueError(
                f"AgentFlow {self.flow_id}: source must be 'skill' or 'dynamic'"
            )

        # Validate predecessor references
        agent_names = {step.agent_name for step in self.steps}
        for i, step in enumerate(self.steps):
            for predecessor in step.predecessors:
                if predecessor not in agent_names:
                    raise ValueError(
                        f"FlowStep {i} ({step.agent_name}): "
                        f"predecessor '{predecessor}' not found in flow"
                    )

                # Find predecessor index
                pred_idx = next(
                    j for j, s in enumerate(self.steps) if s.agent_name == predecessor
                )
                if pred_idx >= i:
                    raise ValueError(
                        f"FlowStep {i} ({step.agent_name}): "
                        f"predecessor '{predecessor}' must come before this step"
                    )

    def get_step_by_agent(self, agent_name: str) -> Optional[FlowStep]:
        """Get a FlowStep by agent name."""
        for step in self.steps:
            if step.agent_name == agent_name:
                return step
        return None

    def get_step_index(self, agent_name: str) -> int:
        """Get the index of a step by agent name. Returns -1 if not found."""
        for i, step in enumerate(self.steps):
            if step.agent_name == agent_name:
                return i
        return -1

    def get_next_step(self, current_agent: str) -> Optional[FlowStep]:
        """Get the next step after the given agent."""
        idx = self.get_step_index(current_agent)
        if idx < 0 or idx >= len(self.steps) - 1:
            return None
        return self.steps[idx + 1]

    def is_last_step(self, agent_name: str) -> bool:
        """Check if the given agent is the last step in the flow."""
        idx = self.get_step_index(agent_name)
        return idx == len(self.steps) - 1
