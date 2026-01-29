"""
Unit tests for flow_invoker.py

Tests the shared flow invocation utility.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ============================================================================
# invoke_agent_flow Tests
# ============================================================================


@pytest.mark.unit
class TestInvokeAgentFlow:
    """Tests for invoke_agent_flow function."""

    def test_invoke_agent_flow_returns_directive(self):
        """invoke_agent_flow should return a directive string."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",  # Must be 'skill' or 'dynamic'
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "MANDATORY DIRECTIVE"
            mock_orchestrator_class.return_value = mock_orchestrator

            result = invoke_agent_flow(
                flow=flow,
                task_id="test123",
                skill_name="perform-tdd",
                phase_id="red",
            )

            assert result == "MANDATORY DIRECTIVE"
            mock_orchestrator.start_flow.assert_called_once()

    def test_invoke_agent_flow_creates_orchestrator_with_params(self):
        """invoke_agent_flow should create ChainOrchestrator with correct params."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        content_dir = Path("/some/content/dir")

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            invoke_agent_flow(
                flow=flow,
                task_id="task123",
                skill_name="perform-tdd",
                phase_id="red",
                domain="technical",
                task_description="Test task",
                skill_content_dir=content_dir,
            )

            mock_orchestrator_class.assert_called_once_with(
                flow=flow,
                task_id="task123",
                skill_content_dir=content_dir,
                skill_name="perform-tdd",
                phase_id="red",
                domain="technical",
                task_description="Test task",
            )

    def test_invoke_agent_flow_default_domain(self):
        """invoke_agent_flow should default domain to 'technical'."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            invoke_agent_flow(
                flow=flow,
                task_id="test123",
                skill_name="test",
                phase_id="test",
            )

            call_kwargs = mock_orchestrator_class.call_args.kwargs
            assert call_kwargs["domain"] == "technical"

    def test_invoke_agent_flow_optional_skill_content_dir(self):
        """invoke_agent_flow should work without skill_content_dir."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="dynamic",  # Test with dynamic source
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            invoke_agent_flow(
                flow=flow,
                task_id="test123",
                skill_name="test",
                phase_id="test",
            )

            call_kwargs = mock_orchestrator_class.call_args.kwargs
            assert call_kwargs["skill_content_dir"] is None

    def test_invoke_agent_flow_with_multi_step_flow(self):
        """invoke_agent_flow should work with multi-step flows."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="multi-step",
            name="Multi Step Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.MULTIPLE_PREDECESSORS,
                    predecessors=("clarification", "research"),
                ),
            ),
        )

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "multi-step directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            result = invoke_agent_flow(
                flow=flow,
                task_id="multi123",
                skill_name="test",
                phase_id="test",
            )

            assert result == "multi-step directive"


# ============================================================================
# get_flow_directive_info Tests
# ============================================================================


@pytest.mark.unit
class TestGetFlowDirectiveInfo:
    """Tests for get_flow_directive_info function."""

    def test_get_flow_directive_info_format(self):
        """get_flow_directive_info should return formatted flow summary."""
        from orchestration.flow_invoker import get_flow_directive_info
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="tdd-red",
            name="TDD RED Phase",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="clarification",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                    predecessors=("clarification",),
                ),
            ),
        )

        result = get_flow_directive_info(flow)

        assert "TDD RED Phase" in result
        assert "tdd-red" in result
        assert "clarification → research" in result
        assert "**Flow:**" in result
        assert "**Agents:**" in result

    def test_get_flow_directive_info_single_agent(self):
        """get_flow_directive_info should handle single agent flow."""
        from orchestration.flow_invoker import get_flow_directive_info
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        flow = AgentFlow(
            flow_id="simple-flow",
            name="Simple Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="generation",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        result = get_flow_directive_info(flow)

        assert "Simple Flow" in result
        assert "generation" in result
        assert "→" not in result  # No arrow for single agent


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.unit
class TestFlowInvokerIntegration:
    """Integration tests for flow_invoker with real TDD flows."""

    def test_invoke_tdd_red_flow(self):
        """invoke_agent_flow should work with real TDD RED flow."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.skills.perform_tdd.flows import TDD_RED_FLOW

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "RED directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            result = invoke_agent_flow(
                flow=TDD_RED_FLOW,
                task_id="tdd123",
                skill_name="perform-tdd",
                phase_id="red",
                task_description="TDD RED phase for test",
            )

            assert result == "RED directive"

    def test_invoke_tdd_green_flow(self):
        """invoke_agent_flow should work with real TDD GREEN flow."""
        from orchestration.flow_invoker import invoke_agent_flow
        from orchestration.skills.perform_tdd.flows import TDD_GREEN_FLOW

        with patch(
            "orchestration.flow_invoker.ChainOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.start_flow.return_value = "GREEN directive"
            mock_orchestrator_class.return_value = mock_orchestrator

            result = invoke_agent_flow(
                flow=TDD_GREEN_FLOW,
                task_id="tdd123",
                skill_name="perform-tdd",
                phase_id="green",
                task_description="TDD GREEN phase",
            )

            assert result == "GREEN directive"

    def test_get_flow_info_for_all_tdd_flows(self):
        """get_flow_directive_info should work for all TDD flows."""
        from orchestration.flow_invoker import get_flow_directive_info
        from orchestration.skills.perform_tdd.flows import TDD_PHASE_FLOWS

        for phase_name, flow in TDD_PHASE_FLOWS.items():
            result = get_flow_directive_info(flow)

            assert flow.name in result
            assert flow.flow_id in result
            # All TDD flows have at least 2 agents
            assert "→" in result or len(flow.steps) == 1
