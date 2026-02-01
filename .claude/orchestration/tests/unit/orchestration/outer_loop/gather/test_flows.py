"""
GATHER Flows Unit Tests

Tests for GATHER agent flow definitions.
"""

import pytest


@pytest.mark.unit
class TestGatherFlow:
    """Tests for GATHER_FLOW definition."""

    def test_flow_exists(self):
        """GATHER_FLOW should exist."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        assert GATHER_FLOW is not None

    def test_flow_has_correct_id(self):
        """Flow should have expected ID."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        assert GATHER_FLOW.flow_id == "outer-loop-gather"

    def test_flow_has_correct_name(self):
        """Flow should have expected name."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        assert GATHER_FLOW.name == "GATHER Phase"

    def test_flow_has_two_steps(self):
        """Flow should have research -> analysis steps."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        assert len(GATHER_FLOW.steps) == 2

    def test_flow_agent_sequence(self):
        """Agents should be in research -> analysis order."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        agents = [step.agent_name for step in GATHER_FLOW.steps]

        assert agents == ["research", "analysis"]

    def test_research_has_workflow_only_context(self):
        """Research step should use WORKFLOW_ONLY context pattern."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        research_step = GATHER_FLOW.steps[0]

        assert research_step.context_pattern == ContextPattern.WORKFLOW_ONLY

    def test_analysis_has_immediate_predecessors(self):
        """Analysis step should use IMMEDIATE_PREDECESSORS context."""
        from orchestration.agent_chain.flow import ContextPattern
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        analysis_step = GATHER_FLOW.steps[1]

        assert analysis_step.context_pattern == ContextPattern.IMMEDIATE_PREDECESSORS
        assert "research" in analysis_step.predecessors

    def test_flow_has_content_files(self):
        """All steps should have content files specified."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        for step in GATHER_FLOW.steps:
            assert step.content_file is not None
            assert len(step.content_file) > 0

    def test_flow_source_is_skill(self):
        """Flow source should be skill."""
        from orchestration.outer_loop.gather.flows import GATHER_FLOW

        assert GATHER_FLOW.source == "skill"


@pytest.mark.unit
class TestGetFlowForDomain:
    """Tests for get_flow_for_domain function."""

    def test_returns_flow_for_any_domain(self):
        """Should return a flow for any domain string."""
        from orchestration.outer_loop.gather.flows import (
            GATHER_FLOW,
            get_flow_for_domain,
        )

        domains = ["CODING", "CORRESPONDENCE", "RESEARCH", "GENERAL", "unknown"]

        for domain in domains:
            flow = get_flow_for_domain(domain)
            assert flow == GATHER_FLOW

    def test_all_domains_use_same_flow(self):
        """All domains should use the same flow structure."""
        from orchestration.outer_loop.gather.flows import get_flow_for_domain

        flow1 = get_flow_for_domain("CODING")
        flow2 = get_flow_for_domain("RESEARCH")
        flow3 = get_flow_for_domain("CORRESPONDENCE")

        assert flow1 == flow2 == flow3
