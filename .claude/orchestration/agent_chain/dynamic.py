"""
Dynamic Flow Creation

Provides functionality for creating agent flows dynamically,
allowing DA to construct flows for novel tasks not covered by
predefined skills.
"""

import uuid
from typing import List, Optional, Tuple

from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
from orchestration.agents.config import is_valid_agent


def create_dynamic_flow(
    name: str,
    agent_sequence: List[str],
    flow_id: Optional[str] = None,
) -> AgentFlow:
    """
    Create a dynamic agent flow from a sequence of agent names.

    Uses sensible defaults for context patterns:
    - First agent: WORKFLOW_ONLY
    - Subsequent agents: IMMEDIATE_PREDECESSORS

    Args:
        name: Human-readable name for the flow
        agent_sequence: List of agent names in execution order
        flow_id: Optional flow ID (auto-generated if not provided)

    Returns:
        AgentFlow instance

    Raises:
        ValueError: If agent sequence is empty or contains invalid agents
    """
    if not agent_sequence:
        raise ValueError("Agent sequence cannot be empty")

    # Validate all agents
    invalid = [a for a in agent_sequence if not is_valid_agent(a)]
    if invalid:
        raise ValueError(f"Invalid agent names: {invalid}")

    # Generate flow ID if not provided
    if not flow_id:
        flow_id = f"dynamic-{uuid.uuid4().hex[:8]}"

    # Build steps with sensible defaults
    steps = []
    for i, agent_name in enumerate(agent_sequence):
        if i == 0:
            # First agent has no predecessors
            step = FlowStep(
                agent_name=agent_name,
                context_pattern=ContextPattern.WORKFLOW_ONLY,
                predecessors=(),
            )
        else:
            # Subsequent agents get context from immediate predecessor
            step = FlowStep(
                agent_name=agent_name,
                context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                predecessors=(agent_sequence[i - 1],),
            )
        steps.append(step)

    return AgentFlow(
        flow_id=flow_id,
        name=name,
        steps=tuple(steps),
        source="dynamic",
    )


def create_dynamic_flow_with_context(
    name: str,
    steps_config: List[Tuple[str, str, List[str]]],
    flow_id: Optional[str] = None,
) -> AgentFlow:
    """
    Create a dynamic agent flow with explicit context configuration.

    Args:
        name: Human-readable name for the flow
        steps_config: List of tuples (agent_name, context_pattern, predecessors)
            - context_pattern: "WORKFLOW_ONLY", "IMMEDIATE_PREDECESSORS", or "MULTIPLE_PREDECESSORS"
        flow_id: Optional flow ID (auto-generated if not provided)

    Returns:
        AgentFlow instance

    Example:
        create_dynamic_flow_with_context(
            name="Custom Analysis Flow",
            steps_config=[
                ("clarification", "WORKFLOW_ONLY", []),
                ("research", "IMMEDIATE_PREDECESSORS", ["clarification"]),
                ("analysis", "MULTIPLE_PREDECESSORS", ["clarification", "research"]),
            ]
        )
    """
    if not steps_config:
        raise ValueError("Steps config cannot be empty")

    # Generate flow ID if not provided
    if not flow_id:
        flow_id = f"dynamic-{uuid.uuid4().hex[:8]}"

    # Build steps
    steps = []
    for agent_name, pattern_str, predecessors in steps_config:
        if not is_valid_agent(agent_name):
            raise ValueError(f"Invalid agent name: {agent_name}")

        try:
            pattern = ContextPattern(pattern_str.lower())
        except ValueError as exc:
            raise ValueError(
                f"Invalid context pattern: {pattern_str}. "
                f"Must be one of: {[p.value for p in ContextPattern]}"
            ) from exc

        step = FlowStep(
            agent_name=agent_name,
            context_pattern=pattern,
            predecessors=tuple(predecessors),
        )
        steps.append(step)

    return AgentFlow(
        flow_id=flow_id,
        name=name,
        steps=tuple(steps),
        source="dynamic",
    )


# Common flow patterns for quick construction


def create_clarify_then_generate(flow_id: Optional[str] = None) -> AgentFlow:
    """
    Create a simple clarification → generation flow.

    Useful for tasks that need requirement clarification
    before generating artifacts.
    """
    return create_dynamic_flow(
        name="Clarify Then Generate",
        agent_sequence=["clarification", "generation"],
        flow_id=flow_id or "clarify-generate",
    )


def create_research_then_synthesize(flow_id: Optional[str] = None) -> AgentFlow:
    """
    Create a research → synthesis flow.

    Useful for information gathering tasks that need
    to consolidate findings.
    """
    return create_dynamic_flow(
        name="Research Then Synthesize",
        agent_sequence=["research", "synthesis"],
        flow_id=flow_id or "research-synthesize",
    )


def create_full_cognitive_flow(flow_id: Optional[str] = None) -> AgentFlow:
    """
    Create a comprehensive flow using all main cognitive agents.

    Flow: clarification → research → analysis → synthesis → generation → validation
    """
    return create_dynamic_flow_with_context(
        name="Full Cognitive Flow",
        steps_config=[
            ("clarification", "WORKFLOW_ONLY", []),
            ("research", "IMMEDIATE_PREDECESSORS", ["clarification"]),
            ("analysis", "IMMEDIATE_PREDECESSORS", ["research"]),
            (
                "synthesis",
                "MULTIPLE_PREDECESSORS",
                ["clarification", "research", "analysis"],
            ),
            ("generation", "IMMEDIATE_PREDECESSORS", ["synthesis"]),
            ("validation", "MULTIPLE_PREDECESSORS", ["synthesis", "generation"]),
        ],
        flow_id=flow_id or "full-cognitive",
    )


def create_analysis_flow(flow_id: Optional[str] = None) -> AgentFlow:
    """
    Create an analysis-focused flow.

    Flow: clarification → research → analysis
    """
    return create_dynamic_flow(
        name="Analysis Flow",
        agent_sequence=["clarification", "research", "analysis"],
        flow_id=flow_id or "analysis-flow",
    )
