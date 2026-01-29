"""
Chain Orchestrator

Manages the execution of agent flows, tracking progress
and generating directives for the next agent in the chain.
"""

from pathlib import Path
from typing import Optional

from orchestration.agent_chain.flow import AgentFlow, FlowStep
from orchestration.agent_chain.state import ChainState
from orchestration.agent_chain.memory import MemoryFile, verify_memory_file_exists
from orchestration.agent_chain.invoker import (
    build_agent_invocation_directive,
    build_task_tool_directive,
)
from orchestration.agents.config import get_agent_config


class ChainOrchestrator:
    """
    Orchestrates the execution of an agent flow.

    Tracks state, validates memory files, and generates
    directives for the next agent in the chain.
    """

    def __init__(
        self,
        flow: AgentFlow,
        task_id: str,
        skill_content_dir: Optional[Path] = None,
        skill_name: Optional[str] = None,
        phase_id: Optional[str] = None,
        domain: str = "technical",
        task_description: str = "",
    ):
        """
        Initialize the orchestrator.

        Args:
            flow: The AgentFlow to execute
            task_id: Unique task identifier
            skill_content_dir: Path to skill's content directory
            skill_name: Name of the skill
            phase_id: Phase ID within the skill
            domain: Task domain
            task_description: Brief task description
        """
        self.flow = flow
        self.task_id = task_id
        self.skill_content_dir = skill_content_dir
        self.skill_name = skill_name
        self.phase_id = phase_id
        self.domain = domain
        self.task_description = task_description

        # Load or create state
        existing_state = ChainState.load(task_id)
        if existing_state and existing_state.flow_id == flow.flow_id:
            self.state = existing_state
        else:
            self.state = ChainState(
                task_id=task_id,
                flow_id=flow.flow_id,
                skill_name=skill_name,
                phase_id=phase_id,
            )

    def start_flow(self) -> str:
        """
        Start the flow by generating the first agent directive.

        Returns:
            Directive for the first agent
        """
        if not self.flow.steps:
            return "Error: Flow has no steps"

        first_step = self.flow.steps[0]
        return self._build_directive_for_step(first_step)

    def get_current_step(self) -> Optional[FlowStep]:
        """
        Get the current step in the flow.

        Returns:
            Current FlowStep or None if flow is complete
        """
        idx = self.state.current_step_index
        if idx >= len(self.flow.steps):
            return None
        return self.flow.steps[idx]

    def get_next_directive(self, completed_agent: str) -> Optional[str]:
        """
        Get the directive for the next agent after one completes.

        This method:
        1. Verifies the completed agent's memory file exists
        2. Updates state to mark agent complete
        3. Advances to next step
        4. Generates directive for next agent (or None if done)

        Args:
            completed_agent: Name of the agent that just completed

        Returns:
            Directive for next agent, or None if flow is complete
        """
        # Verify memory file exists
        if not verify_memory_file_exists(self.task_id, completed_agent):
            memory_path = MemoryFile.get_path(self.task_id, completed_agent)
            return f"Error: Memory file required but not found: {memory_path}"

        # Mark agent complete
        memory_path = str(MemoryFile.get_path(self.task_id, completed_agent))
        self.state.mark_agent_complete(completed_agent, memory_path)
        self.state.advance_step()
        self.state.save()

        # Check if flow is complete
        if self.is_flow_complete():
            return None

        # Get next step
        next_step = self.get_current_step()
        if not next_step:
            return None

        # Handle conditional steps
        if next_step.conditional:
            # For now, always execute conditional steps
            # Future: check runtime conditions
            pass

        return self._build_directive_for_step(next_step)

    def is_flow_complete(self) -> bool:
        """Check if the flow has completed all steps."""
        return self.state.current_step_index >= len(self.flow.steps)

    def _build_directive_for_step(self, step: FlowStep) -> str:
        """
        Build a complete directive for a flow step.

        Checks if this is the first invocation for the agent and includes
        the MANDATORY learnings directive if so.

        Args:
            step: The FlowStep to build directive for

        Returns:
            Complete directive string
        """
        # Check if this agent needs learnings directive
        include_learnings = self.state.needs_learnings_directive(step.agent_name)

        # If injecting learnings, mark it BEFORE building (in case of crash)
        if include_learnings:
            self.state.mark_learnings_injected(step.agent_name)
            self.state.save()  # Persist immediately

        # Build the agent invocation directive
        directive = build_agent_invocation_directive(
            task_id=self.task_id,
            agent_name=step.agent_name,
            flow_id=self.flow.flow_id,
            content_file=step.content_file,
            predecessors=list(step.predecessors),
            skill_content_dir=self.skill_content_dir,
            skill_name=self.skill_name,
            phase_id=self.phase_id,
            domain=self.domain,
            task_description=self.task_description,
            include_learnings_directive=include_learnings,
        )

        # Get model from agent config
        agent_config = get_agent_config(step.agent_name)
        model = agent_config.get("model") if agent_config else None

        # Wrap in Task tool directive
        return build_task_tool_directive(
            task_id=self.task_id,
            agent_name=step.agent_name,
            prompt=directive,
            model=model,
        )

    def save(self) -> Path:
        """Save the current state."""
        return self.state.save()

    def get_completed_agents(self) -> list:
        """Get list of completed agent names."""
        return self.state.completed_agents.copy()

    def get_memory_files(self) -> dict:
        """Get dict of agent names to memory file paths."""
        return self.state.memory_files_created.copy()


def load_orchestrator(
    task_id: str,
    flow: AgentFlow,
    skill_content_dir: Optional[Path] = None,
    skill_name: Optional[str] = None,
    phase_id: Optional[str] = None,
    domain: str = "technical",
    task_description: str = "",
) -> ChainOrchestrator:
    """
    Load or create a ChainOrchestrator for a task.

    Args:
        task_id: Task identifier
        flow: AgentFlow to execute
        skill_content_dir: Path to skill's content directory
        skill_name: Name of the skill
        phase_id: Phase ID within the skill
        domain: Task domain
        task_description: Brief task description

    Returns:
        ChainOrchestrator instance
    """
    return ChainOrchestrator(
        flow=flow,
        task_id=task_id,
        skill_content_dir=skill_content_dir,
        skill_name=skill_name,
        phase_id=phase_id,
        domain=domain,
        task_description=task_description,
    )
