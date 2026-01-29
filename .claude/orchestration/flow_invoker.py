"""
Flow Invoker - Shared utility for triggering agent flows.

Any phase entry point or advance script can use this to invoke
the appropriate agent flow for their context.

This is THE single entry point for triggering any agent flow.
All phase entry points and advance scripts should use this.
"""

from pathlib import Path
from typing import Optional

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
