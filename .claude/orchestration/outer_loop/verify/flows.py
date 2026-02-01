"""
VERIFY Phase Flows

Defines agent flows for output verification against IDEAL STATE.
Flow: validation agent only
"""

from orchestration.agent_chain.flow import AgentFlow, ContextPattern, FlowStep

# VERIFY flow: single validation agent
# Validation agent compares output against IDEAL STATE criteria
VERIFY_FLOW = AgentFlow(
    flow_id="outer-loop-verify",
    name="VERIFY Phase",
    steps=(
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=(),
            content_file="verify/verification.md",
            conditional=False,
        ),
    ),
    source="skill",
)


def get_verify_flow() -> AgentFlow:
    """
    Get the agent flow for VERIFY phase.

    Returns:
        AgentFlow for verification
    """
    return VERIFY_FLOW
