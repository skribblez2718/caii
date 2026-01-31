"""
Scaffold-Docs Flow Definitions

Defines the agent flows for scaffold-docs skill:
- SCAFFOLD_FLOW: clarification → analysis → synthesis → validation (create mode)
- UPDATE_FLOW: analysis → synthesis → validation (update mode)
"""

from typing import Literal

from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

# SCAFFOLD Flow: Create new documentation
# Flow: clarification → analysis → synthesis → validation
SCAFFOLD_FLOW = AgentFlow(
    flow_id="scaffold-docs-scaffold",
    name="Scaffold Documentation",
    source="skill",
    steps=(
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="scaffold/clarification.md",
        ),
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="scaffold/analysis.md",
        ),
        FlowStep(
            agent_name="synthesis",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("clarification", "analysis"),
            content_file="scaffold/synthesis.md",
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("clarification", "analysis", "synthesis"),
            content_file="scaffold/validation.md",
        ),
    ),
)


# UPDATE Flow: Update existing documentation
# Flow: analysis → synthesis → validation
UPDATE_FLOW = AgentFlow(
    flow_id="scaffold-docs-update",
    name="Update Documentation",
    source="skill",
    steps=(
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="update/analysis.md",
        ),
        FlowStep(
            agent_name="synthesis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="update/synthesis.md",
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("analysis", "synthesis"),
            content_file="update/validation.md",
        ),
    ),
)


# Mapping from mode to flow
MODE_FLOWS = {
    "scaffold": SCAFFOLD_FLOW,
    "update": UPDATE_FLOW,
}


def get_flow_for_mode(mode: Literal["scaffold", "update"]) -> AgentFlow:
    """
    Get the agent flow for a scaffold-docs mode.

    Args:
        mode: Operation mode ('scaffold' or 'update')

    Returns:
        AgentFlow for the mode

    Raises:
        ValueError: If mode is invalid
    """
    flow = MODE_FLOWS.get(mode)
    if not flow:
        valid = list(MODE_FLOWS.keys())
        raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid}")
    return flow
