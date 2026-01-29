"""
Unit tests for agent_chain/flow.py
"""

import pytest

from orchestration.agent_chain.flow import (
    AgentFlow,
    FlowStep,
    ContextPattern,
)


class TestFlowStep:
    """Tests for FlowStep dataclass."""

    def test_workflow_only_no_predecessors(self):
        """WORKFLOW_ONLY pattern should not have predecessors."""
        step = FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            predecessors=(),
        )
        assert step.agent_name == "clarification"
        assert step.context_pattern == ContextPattern.WORKFLOW_ONLY
        assert step.predecessors == ()

    def test_workflow_only_with_predecessors_raises(self):
        """WORKFLOW_ONLY with predecessors should raise ValueError."""
        with pytest.raises(ValueError, match="should not have predecessors"):
            FlowStep(
                agent_name="clarification",
                context_pattern=ContextPattern.WORKFLOW_ONLY,
                predecessors=("research",),
            )

    def test_immediate_predecessors_single(self):
        """IMMEDIATE_PREDECESSORS should have at most one predecessor."""
        step = FlowStep(
            agent_name="research",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
        )
        assert step.predecessors == ("clarification",)

    def test_immediate_predecessors_multiple_raises(self):
        """IMMEDIATE_PREDECESSORS with multiple predecessors should raise."""
        with pytest.raises(ValueError, match="at most one predecessor"):
            FlowStep(
                agent_name="research",
                context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                predecessors=("clarification", "analysis"),
            )

    def test_multiple_predecessors_valid(self):
        """MULTIPLE_PREDECESSORS should have at least two predecessors."""
        step = FlowStep(
            agent_name="synthesis",
            context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
            predecessors=("clarification", "research"),
        )
        assert step.predecessors == ("clarification", "research")

    def test_multiple_predecessors_too_few_raises(self):
        """MULTIPLE_PREDECESSORS with fewer than 2 predecessors should raise."""
        with pytest.raises(ValueError, match="at least two predecessors"):
            FlowStep(
                agent_name="synthesis",
                context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
                predecessors=("clarification",),
            )

    def test_conditional_flag(self):
        """Conditional flag should be set correctly."""
        step = FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            conditional=True,
        )
        assert step.conditional is True

    def test_content_file(self):
        """Content file should be set correctly."""
        step = FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            content_file="red/clarification.md",
        )
        assert step.content_file == "red/clarification.md"


class TestAgentFlow:
    """Tests for AgentFlow dataclass."""

    def test_valid_flow(self):
        """Valid flow should be created successfully."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )
        assert flow.flow_id == "test-flow"
        assert flow.name == "Test Flow"
        assert len(flow.steps) == 2

    def test_empty_steps_raises(self):
        """Flow with no steps should raise ValueError."""
        with pytest.raises(ValueError, match="at least one step"):
            AgentFlow(
                flow_id="empty-flow",
                name="Empty Flow",
                steps=(),
            )

    def test_invalid_source_raises(self):
        """Invalid source should raise ValueError."""
        with pytest.raises(ValueError, match="must be 'skill' or 'dynamic'"):
            AgentFlow(
                flow_id="test-flow",
                name="Test Flow",
                steps=(
                    FlowStep(
                        agent_name="clarification",
                        context_pattern=ContextPattern.WORKFLOW_ONLY,
                    ),
                ),
                source="invalid",
            )

    def test_predecessor_not_in_flow_raises(self):
        """Predecessor not in flow should raise ValueError."""
        with pytest.raises(ValueError, match="not found in flow"):
            AgentFlow(
                flow_id="test-flow",
                name="Test Flow",
                steps=(
                    FlowStep(
                        agent_name="research",
                        context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                        predecessors=("nonexistent",),
                    ),
                ),
            )

    def test_predecessor_after_step_raises(self):
        """Predecessor that comes after the step should raise ValueError."""
        with pytest.raises(ValueError, match="must come before"):
            AgentFlow(
                flow_id="test-flow",
                name="Test Flow",
                steps=(
                    FlowStep(
                        agent_name="research",
                        context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                        predecessors=("clarification",),
                    ),
                    FlowStep(
                        agent_name="clarification",
                        context_pattern=ContextPattern.WORKFLOW_ONLY,
                    ),
                ),
            )

    def test_get_step_by_agent(self):
        """get_step_by_agent should return correct step."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )
        step = flow.get_step_by_agent("research")
        assert step is not None
        assert step.agent_name == "research"

    def test_get_step_by_agent_not_found(self):
        """get_step_by_agent should return None if not found."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
            ),
        )
        assert flow.get_step_by_agent("nonexistent") is None

    def test_get_step_index(self):
        """get_step_index should return correct index."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )
        assert flow.get_step_index("clarification") == 0
        assert flow.get_step_index("research") == 1
        assert flow.get_step_index("nonexistent") == -1

    def test_get_next_step(self):
        """get_next_step should return correct next step."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )
        next_step = flow.get_next_step("clarification")
        assert next_step is not None
        assert next_step.agent_name == "research"

    def test_get_next_step_last(self):
        """get_next_step should return None for last step."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
            ),
        )
        assert flow.get_next_step("clarification") is None

    def test_is_last_step(self):
        """is_last_step should return correct value."""
        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )
        assert flow.is_last_step("clarification") is False
        assert flow.is_last_step("research") is True
