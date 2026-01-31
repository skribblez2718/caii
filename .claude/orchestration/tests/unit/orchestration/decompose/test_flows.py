"""
Unit tests for decompose/flows.py

Tests the DECOMPOSE protocol flow definitions:
- DECOMPOSE_FLOW: clarification → analysis → synthesis → validation
- AGGREGATION_FLOW: synthesis (single step)
"""

import pytest


@pytest.mark.unit
class TestDecomposeFlow:
    """Tests for DECOMPOSE_FLOW definition."""

    def test_decompose_flow_exists(self):
        """DECOMPOSE_FLOW should be importable."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        assert DECOMPOSE_FLOW is not None

    def test_decompose_flow_has_correct_id(self):
        """DECOMPOSE_FLOW should have correct flow_id."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        assert DECOMPOSE_FLOW.flow_id == "decompose-protocol"

    def test_decompose_flow_has_correct_name(self):
        """DECOMPOSE_FLOW should have correct name."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        assert DECOMPOSE_FLOW.name == "Task Decomposition Protocol"

    def test_decompose_flow_has_four_steps(self):
        """DECOMPOSE_FLOW should have 4 steps."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        assert len(DECOMPOSE_FLOW.steps) == 4

    def test_decompose_flow_agent_sequence(self):
        """DECOMPOSE_FLOW should have correct agent sequence."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        agents = [step.agent_name for step in DECOMPOSE_FLOW.steps]
        assert agents == ["clarification", "analysis", "synthesis", "validation"]

    def test_decompose_flow_clarification_is_conditional(self):
        """Clarification step should be conditional."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        clarification_step = DECOMPOSE_FLOW.steps[0]
        assert clarification_step.conditional is True

    def test_decompose_flow_clarification_has_workflow_only_pattern(self):
        """Clarification step should use WORKFLOW_ONLY pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        clarification_step = DECOMPOSE_FLOW.steps[0]
        assert clarification_step.context_pattern == ContextPattern.WORKFLOW_ONLY

    def test_decompose_flow_analysis_has_immediate_predecessors(self):
        """Analysis step should use IMMEDIATE_PREDECESSORS pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        analysis_step = DECOMPOSE_FLOW.steps[1]
        assert analysis_step.context_pattern == ContextPattern.IMMEDIATE_PREDECESSORS
        assert analysis_step.predecessors == ("clarification",)

    def test_decompose_flow_synthesis_has_immediate_predecessors(self):
        """Synthesis step should use IMMEDIATE_PREDECESSORS pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        synthesis_step = DECOMPOSE_FLOW.steps[2]
        assert synthesis_step.context_pattern == ContextPattern.IMMEDIATE_PREDECESSORS
        assert synthesis_step.predecessors == ("analysis",)

    def test_decompose_flow_validation_has_multiple_predecessors(self):
        """Validation step should use MULTIPLE_PREDECESSORS pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        validation_step = DECOMPOSE_FLOW.steps[3]
        assert validation_step.context_pattern == ContextPattern.MULTIPLE_PREDECESSORS
        assert set(validation_step.predecessors) == {"analysis", "synthesis"}

    def test_decompose_flow_has_content_files(self):
        """All steps should have content files defined."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        for step in DECOMPOSE_FLOW.steps:
            assert step.content_file is not None
            assert step.content_file.startswith("decompose/")

    def test_decompose_flow_source_is_skill(self):
        """DECOMPOSE_FLOW source should be 'skill'."""
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        assert DECOMPOSE_FLOW.source == "skill"


@pytest.mark.unit
class TestAggregationFlow:
    """Tests for AGGREGATION_FLOW definition."""

    def test_aggregation_flow_exists(self):
        """AGGREGATION_FLOW should be importable."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert AGGREGATION_FLOW is not None

    def test_aggregation_flow_has_correct_id(self):
        """AGGREGATION_FLOW should have correct flow_id."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert AGGREGATION_FLOW.flow_id == "decompose-aggregation"

    def test_aggregation_flow_has_correct_name(self):
        """AGGREGATION_FLOW should have correct name."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert AGGREGATION_FLOW.name == "Subtask Result Aggregation"

    def test_aggregation_flow_has_one_step(self):
        """AGGREGATION_FLOW should have 1 step."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert len(AGGREGATION_FLOW.steps) == 1

    def test_aggregation_flow_uses_synthesis_agent(self):
        """AGGREGATION_FLOW should use synthesis agent."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert AGGREGATION_FLOW.steps[0].agent_name == "synthesis"

    def test_aggregation_flow_synthesis_has_workflow_only_pattern(self):
        """Synthesis step should use WORKFLOW_ONLY pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.decompose.flows import AGGREGATION_FLOW

        synthesis_step = AGGREGATION_FLOW.steps[0]
        assert synthesis_step.context_pattern == ContextPattern.WORKFLOW_ONLY

    def test_aggregation_flow_has_content_file(self):
        """Synthesis step should have content file."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        synthesis_step = AGGREGATION_FLOW.steps[0]
        assert synthesis_step.content_file == "aggregation/synthesis.md"

    def test_aggregation_flow_source_is_skill(self):
        """AGGREGATION_FLOW source should be 'skill'."""
        from orchestration.decompose.flows import AGGREGATION_FLOW

        assert AGGREGATION_FLOW.source == "skill"


@pytest.mark.unit
class TestFlowValidation:
    """Tests for flow validation at import time."""

    def test_flows_pass_predecessor_validation(self):
        """Both flows should pass predecessor validation."""
        # This test passes if import succeeds without ValueError
        from orchestration.decompose.flows import AGGREGATION_FLOW, DECOMPOSE_FLOW

        # If we get here, validation passed
        assert DECOMPOSE_FLOW is not None
        assert AGGREGATION_FLOW is not None
