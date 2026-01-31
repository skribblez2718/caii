"""
DECOMPOSE Protocol Flow Definitions

Defines the agent flows for task decomposition:
- DECOMPOSE_FLOW: clarification → analysis → synthesis → validation
- AGGREGATION_FLOW: synthesis (combines subtask results)
"""

from orchestration.agent_chain.flow import AgentFlow, ContextPattern, FlowStep

# DECOMPOSE Protocol Flow
# Breaks complex/very_complex tasks into SIMPLE subtasks
DECOMPOSE_FLOW = AgentFlow(
    flow_id="decompose-protocol",
    name="Task Decomposition Protocol",
    source="skill",
    steps=(
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="decompose/clarification.md",
            conditional=True,  # Skip if scope is already clear
        ),
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="decompose/analysis.md",
        ),
        FlowStep(
            agent_name="synthesis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="decompose/synthesis.md",
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("analysis", "synthesis"),
            content_file="decompose/validation.md",
        ),
    ),
)


# Aggregation Flow
# Combines subtask outputs into unified deliverable
AGGREGATION_FLOW = AgentFlow(
    flow_id="decompose-aggregation",
    name="Subtask Result Aggregation",
    source="skill",
    steps=(
        FlowStep(
            agent_name="synthesis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="aggregation/synthesis.md",
        ),
    ),
)
