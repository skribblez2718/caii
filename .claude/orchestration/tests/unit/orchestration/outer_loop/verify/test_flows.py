"""
Unit tests for outer_loop/verify/flows.py

Tests the VERIFY_FLOW AgentFlow definition.
"""

import pytest

from orchestration.agent_chain.flow import AgentFlow, ContextPattern, FlowStep


class TestVerifyFlowStructure:
    """Tests for VERIFY_FLOW AgentFlow definition."""

    @pytest.mark.unit
    def test_verify_flow_exists(self):
        """VERIFY_FLOW should be importable from flows module."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        assert isinstance(VERIFY_FLOW, AgentFlow)

    @pytest.mark.unit
    def test_verify_flow_has_correct_flow_id(self):
        """VERIFY_FLOW should have flow_id='outer-loop-verify'."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        assert VERIFY_FLOW.flow_id == "outer-loop-verify"

    @pytest.mark.unit
    def test_verify_flow_has_correct_name(self):
        """VERIFY_FLOW should have name='VERIFY Phase'."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        assert VERIFY_FLOW.name == "VERIFY Phase"

    @pytest.mark.unit
    def test_verify_flow_has_skill_source(self):
        """VERIFY_FLOW should have source='skill'."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        assert VERIFY_FLOW.source == "skill"

    @pytest.mark.unit
    def test_verify_flow_has_validation_agent(self):
        """VERIFY_FLOW should have a validation agent step."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        agent_names = [step.agent_name for step in VERIFY_FLOW.steps]
        assert "validation" in agent_names

    @pytest.mark.unit
    def test_verify_flow_step_count(self):
        """VERIFY_FLOW should have exactly one step (validation only)."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        assert len(VERIFY_FLOW.steps) == 1

    @pytest.mark.unit
    def test_verify_flow_validation_step_content_file(self):
        """Validation step should use verification.md content file."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        validation_step = VERIFY_FLOW.steps[0]
        assert validation_step.content_file == "verify/verification.md"

    @pytest.mark.unit
    def test_verify_flow_validation_step_context_pattern(self):
        """Validation step should use IMMEDIATE_PREDECESSORS context pattern."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        validation_step = VERIFY_FLOW.steps[0]
        assert validation_step.context_pattern == ContextPattern.IMMEDIATE_PREDECESSORS

    @pytest.mark.unit
    def test_verify_flow_validation_step_not_conditional(self):
        """Validation step should not be conditional."""
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        validation_step = VERIFY_FLOW.steps[0]
        assert validation_step.conditional is False
