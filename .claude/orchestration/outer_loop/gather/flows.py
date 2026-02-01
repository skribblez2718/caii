"""
GATHER Phase Flows

Defines agent flows for dynamic state gathering.
All domains use research -> analysis pattern, but with
domain-specific content files.
"""

from orchestration.agent_chain.flow import AgentFlow, ContextPattern, FlowStep

# GATHER flow: research -> analysis
# Research gathers domain-specific state information
# Analysis structures and prioritizes the state data
GATHER_FLOW = AgentFlow(
    flow_id="outer-loop-gather",
    name="GATHER Phase",
    steps=(
        FlowStep(
            agent_name="research",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="gather/research.md",
            conditional=False,
        ),
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("research",),
            content_file="gather/analysis.md",
            conditional=False,
        ),
    ),
    source="skill",
)


def get_flow_for_domain(domain: str) -> AgentFlow:  # pylint: disable=unused-argument
    """
    Get the agent flow for a given domain.

    Currently all domains use the same flow structure
    (research -> analysis) but with different content.
    The domain is used to select domain-specific content files.

    Args:
        domain: Task domain (e.g., "CODING", "CORRESPONDENCE")

    Returns:
        AgentFlow for state gathering
    """
    # All domains use the same flow structure
    # Domain-specific behavior comes from content files
    return GATHER_FLOW
