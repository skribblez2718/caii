"""
Flow Invoker - Shared utility for triggering agent flows.

Any phase entry point or advance script can use this to invoke
the appropriate agent flow for their context.

This is THE single entry point for triggering any agent flow.
All phase entry points and advance scripts should use this.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from orchestration.agent_chain.flow import AgentFlow
from orchestration.agent_chain.orchestrator import ChainOrchestrator


def invoke_agent_flow(
    flow: AgentFlow,
    task_id: str,
    skill_name: str,
    phase_id: str,
    domain: str = "technical",
    task_description: str = "",
    skill_content_dir: Optional[Path] = None,
) -> str:
    """
    Invoke an agent flow and return the directive for DA to execute.

    This is the single entry point for triggering any agent flow.
    All phase entry points and advance scripts should use this.

    Args:
        flow: The AgentFlow to execute
        task_id: Unique task identifier (session_id)
        skill_name: Name of the skill (e.g., "tdd", "gather")
        phase_id: Phase within the skill (e.g., "red", "green")
        domain: Task domain (default: "technical")
        task_description: Brief task description
        skill_content_dir: Path to skill's content directory

    Returns:
        Complete directive string with MANDATORY agent invocation

    Note:
        AgentFlow dataclass enforces that flows have at least one step,
        so empty flow validation happens at flow creation time.
    """
    orchestrator = ChainOrchestrator(
        flow=flow,
        task_id=task_id,
        skill_content_dir=skill_content_dir,
        skill_name=skill_name,
        phase_id=phase_id,
        domain=domain,
        task_description=task_description,
    )

    return orchestrator.start_flow()


def get_flow_directive_info(flow: AgentFlow) -> str:
    """
    Get a summary of the flow for display purposes.

    Args:
        flow: The AgentFlow to summarize

    Returns:
        Formatted string with flow name, ID, and agent sequence
    """
    agents = " → ".join(s.agent_name for s in flow.steps)
    return f"**Flow:** {flow.name} (`{flow.flow_id}`)\n**Agents:** {agents}"


def is_flow_complete(task_id: str, flow_id: str) -> bool:
    """
    Check if a flow has completed all agents.

    Used by advance scripts to validate before phase advancement.

    Args:
        task_id: Task/session ID
        flow_id: Flow ID to check

    Returns:
        True if all agents in the flow have completed
    """
    from orchestration.agent_chain.state import ChainState
    from orchestration.flow_registry import get_flow

    state = ChainState.load(task_id)
    if not state:
        return False

    # State might be from a different flow (e.g., previous phase)
    if state.flow_id != flow_id:
        return False

    flow = get_flow(flow_id)
    if not flow:
        return False

    return state.current_step_index >= len(flow.steps)


def get_flow_completion_status(task_id: str, flow_id: str) -> Dict[str, Any]:
    """
    Get detailed flow completion status.

    Args:
        task_id: Task/session ID
        flow_id: Flow ID to check

    Returns:
        Dict with completion info: is_complete, completed_agents, total_agents
    """
    from orchestration.agent_chain.state import ChainState
    from orchestration.flow_registry import get_flow

    state = ChainState.load(task_id)
    flow = get_flow(flow_id)

    if not state or not flow:
        return {
            "is_complete": False,
            "completed_agents": [],
            "total_agents": 0,
            "error": "State or flow not found",
        }

    return {
        "is_complete": state.current_step_index >= len(flow.steps),
        "completed_agents": state.completed_agents,
        "total_agents": len(flow.steps),
        "current_index": state.current_step_index,
    }
