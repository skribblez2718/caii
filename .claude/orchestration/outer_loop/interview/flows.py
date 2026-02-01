"""
INTERVIEW Phase Flows

Defines agent flows for IDEAL STATE capture with iterative refinement.
Flow: clarification -> research (optional) -> validation
"""

from orchestration.agent_chain.flow import AgentFlow, ContextPattern, FlowStep

# INTERVIEW flow: clarification -> validation
# Clarification uses Johari to capture requirements and generate questions
# Validation scores completeness and identifies gaps
INTERVIEW_FLOW = AgentFlow(
    flow_id="outer-loop-interview",
    name="INTERVIEW Phase",
    steps=(
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="interview/clarification.md",
            conditional=False,
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="interview/validation.md",
            conditional=False,
        ),
    ),
    source="skill",
)

# Refinement flow for iterations after initial
# Uses analysis to identify specific gaps, then clarification to address
INTERVIEW_REFINEMENT_FLOW = AgentFlow(
    flow_id="outer-loop-interview-refinement",
    name="INTERVIEW Refinement",
    steps=(
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="interview/refinement_analysis.md",
            conditional=False,
        ),
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="interview/refinement_clarification.md",
            conditional=False,
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="interview/validation.md",
            conditional=False,
        ),
    ),
    source="skill",
)


def get_interview_flow(iteration: int = 0) -> AgentFlow:
    """
    Get appropriate flow based on iteration.

    Args:
        iteration: Current interview iteration (0 = initial)

    Returns:
        AgentFlow for this iteration
    """
    if iteration == 0:
        return INTERVIEW_FLOW
    return INTERVIEW_REFINEMENT_FLOW
