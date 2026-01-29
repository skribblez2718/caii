"""
TDD Phase Flow Definitions

Defines the agent flows for each TDD phase:
- RED: clarification → research → analysis → generation (write failing test)
- GREEN: analysis → generation → validation (implement to pass)
- REFACTOR: analysis → generation → validation (improve quality)
- DOC: analysis → generation (update documentation)
"""

from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

# RED Phase: Write Failing Test
# Flow: clarification (conditional) → research → analysis → generation
TDD_RED_FLOW = AgentFlow(
    flow_id="perform-tdd-red",
    name="TDD RED Phase",
    source="skill",
    steps=(
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="red/clarification.md",
            conditional=True,  # Skip if requirements are clear
        ),
        FlowStep(
            agent_name="research",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="red/research.md",
        ),
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("research",),
            content_file="red/analysis.md",
        ),
        FlowStep(
            agent_name="generation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("clarification", "research", "analysis"),
            content_file="red/generation.md",
        ),
    ),
)


# GREEN Phase: Implement to Pass
# Flow: analysis → generation → validation
TDD_GREEN_FLOW = AgentFlow(
    flow_id="perform-tdd-green",
    name="TDD GREEN Phase",
    source="skill",
    steps=(
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="green/analysis.md",
        ),
        FlowStep(
            agent_name="generation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="green/generation.md",
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("analysis", "generation"),
            content_file="green/validation.md",
        ),
    ),
)


# REFACTOR Phase: Improve Quality
# Flow: analysis → generation → validation
TDD_REFACTOR_FLOW = AgentFlow(
    flow_id="perform-tdd-refactor",
    name="TDD REFACTOR Phase",
    source="skill",
    steps=(
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="refactor/analysis.md",
        ),
        FlowStep(
            agent_name="generation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="refactor/generation.md",
        ),
        FlowStep(
            agent_name="validation",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("analysis", "generation"),
            content_file="refactor/validation.md",
        ),
    ),
)


# DOC Phase: Update Documentation
# Flow: analysis → generation
TDD_DOC_FLOW = AgentFlow(
    flow_id="perform-tdd-doc",
    name="TDD DOC Phase",
    source="skill",
    steps=(
        FlowStep(
            agent_name="analysis",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
            content_file="doc/analysis.md",
        ),
        FlowStep(
            agent_name="generation",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("analysis",),
            content_file="doc/generation.md",
        ),
    ),
)


# Mapping from TDD phase to flow
TDD_PHASE_FLOWS = {
    "RED": TDD_RED_FLOW,
    "GREEN": TDD_GREEN_FLOW,
    "REFACTOR": TDD_REFACTOR_FLOW,
    "DOC": TDD_DOC_FLOW,
}


def get_flow_for_phase(phase_name: str) -> AgentFlow:
    """
    Get the agent flow for a TDD phase.

    Args:
        phase_name: Name of the phase (RED, GREEN, REFACTOR, DOC)

    Returns:
        AgentFlow for the phase

    Raises:
        ValueError: If phase name is invalid
    """
    flow = TDD_PHASE_FLOWS.get(phase_name.upper())
    if not flow:
        valid = list(TDD_PHASE_FLOWS.keys())
        raise ValueError(f"Invalid phase: {phase_name}. Valid phases: {valid}")
    return flow
