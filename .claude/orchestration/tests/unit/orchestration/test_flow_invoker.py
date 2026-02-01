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


# ============================================================================
# is_flow_complete Tests
# ============================================================================


@pytest.mark.unit
class TestIsFlowComplete:
    """Tests for is_flow_complete function."""

    def test_is_flow_complete_returns_false_when_not_started(self):
        """is_flow_complete should return False when flow hasn't started."""
        from orchestration.flow_invoker import is_flow_complete

        # No state exists for this task
        result = is_flow_complete("nonexistent-task-id", "perform-tdd-red")

        assert result is False

    def test_is_flow_complete_returns_false_when_in_progress(self):
        """is_flow_complete should return False when agents still pending."""
        from orchestration.flow_invoker import is_flow_complete
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        task_id = "test-in-progress-123"
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=1,  # Only 1 agent done, RED has 4
            completed_agents=["clarification"],
        )
        state.save()

        try:
            result = is_flow_complete(task_id, "perform-tdd-red")
            assert result is False
        finally:
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()

    def test_is_flow_complete_returns_true_when_all_agents_done(self):
        """is_flow_complete should return True when all agents completed."""
        from orchestration.flow_invoker import is_flow_complete
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.skills.perform_tdd.flows import TDD_DOC_FLOW

        task_id = "test-complete-789"
        # DOC flow has 2 agents (analysis, generation)
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-doc",
            skill_name="perform-tdd",
            phase_id="doc",
            current_step_index=2,  # Both agents done
            completed_agents=["analysis", "generation"],
        )
        state.save()

        try:
            result = is_flow_complete(task_id, "perform-tdd-doc")
            assert result is True
        finally:
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()

    def test_is_flow_complete_returns_false_for_wrong_flow_id(self):
        """is_flow_complete should return False if state has different flow_id."""
        from orchestration.flow_invoker import is_flow_complete
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        task_id = "test-wrong-flow-456"
        # State is for GREEN but we ask about RED
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-green",
            skill_name="perform-tdd",
            phase_id="green",
            current_step_index=3,
            completed_agents=["analysis", "generation", "validation"],
        )
        state.save()

        try:
            result = is_flow_complete(task_id, "perform-tdd-red")
            assert result is False
        finally:
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()


# ============================================================================
# get_flow_completion_status Tests
# ============================================================================


@pytest.mark.unit
class TestGetFlowCompletionStatus:
    """Tests for get_flow_completion_status function."""

    def test_get_flow_completion_status_returns_error_for_missing_state(self):
        """get_flow_completion_status should return error for missing state."""
        from orchestration.flow_invoker import get_flow_completion_status

        result = get_flow_completion_status("nonexistent", "perform-tdd-red")

        assert result["is_complete"] is False
        assert "error" in result

    def test_get_flow_completion_status_returns_detailed_info(self):
        """get_flow_completion_status should return detailed completion info."""
        from orchestration.flow_invoker import get_flow_completion_status
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        task_id = "test-status-detail"
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-doc",
            skill_name="perform-tdd",
            phase_id="doc",
            current_step_index=1,
            completed_agents=["analysis"],
        )
        state.save()

        try:
            result = get_flow_completion_status(task_id, "perform-tdd-doc")

            assert result["is_complete"] is False
            assert result["completed_agents"] == ["analysis"]
            assert result["total_agents"] == 2  # DOC has 2 agents
            assert result["current_index"] == 1
        finally:
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()
