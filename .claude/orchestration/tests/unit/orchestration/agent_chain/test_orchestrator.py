"""
Unit tests for agent_chain/orchestrator.py
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestration.agent_chain.orchestrator import ChainOrchestrator, load_orchestrator
from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
from orchestration.agent_chain.state import ChainState


@pytest.fixture
def simple_flow():
    """Create a simple two-step flow for testing."""
    return AgentFlow(
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


@pytest.fixture
def flow_with_repeated_agent():
    """Create a flow where same agent appears twice."""
    return AgentFlow(
        flow_id="repeat-flow",
        name="Repeat Flow",
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
            FlowStep(
                agent_name="clarification",
                context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
                predecessors=("research",),
            ),
        ),
    )


class TestChainOrchestratorLearnings:
    """Tests for learnings injection in ChainOrchestrator."""

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    @patch("orchestration.agent_chain.orchestrator.build_agent_invocation_directive")
    @patch("orchestration.agent_chain.orchestrator.build_task_tool_directive")
    def test_first_agent_gets_learnings_directive(
        self, mock_task_directive, mock_agent_directive, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """First invocation of an agent should include learnings directive."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}
        mock_agent_directive.return_value = "agent directive"
        mock_task_directive.return_value = "task directive"

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        orchestrator.start_flow()

        # Verify build_agent_invocation_directive was called with include_learnings_directive=True
        call_kwargs = mock_agent_directive.call_args[1]
        assert call_kwargs["include_learnings_directive"] is True
        assert call_kwargs["agent_name"] == "clarification"

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    @patch("orchestration.agent_chain.orchestrator.build_agent_invocation_directive")
    @patch("orchestration.agent_chain.orchestrator.build_task_tool_directive")
    @patch("orchestration.agent_chain.orchestrator.verify_memory_file_exists")
    def test_second_invocation_same_agent_no_learnings(
        self, mock_verify, mock_task_directive, mock_agent_directive, mock_config,
        flow_with_repeated_agent, tmp_path, monkeypatch
    ):
        """Second invocation of same agent should NOT include learnings directive."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}
        mock_agent_directive.return_value = "agent directive"
        mock_task_directive.return_value = "task directive"
        mock_verify.return_value = True

        orchestrator = ChainOrchestrator(
            flow=flow_with_repeated_agent,
            task_id="test-123",
        )

        # Start flow (clarification - first time)
        orchestrator.start_flow()

        # Clear mock to track subsequent calls
        mock_agent_directive.reset_mock()

        # Advance past clarification
        orchestrator.get_next_directive("clarification")

        # Clear mock again
        mock_agent_directive.reset_mock()

        # Advance past research
        orchestrator.get_next_directive("research")

        # Now on second clarification invocation
        call_kwargs = mock_agent_directive.call_args[1]
        assert call_kwargs["include_learnings_directive"] is False
        assert call_kwargs["agent_name"] == "clarification"

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    @patch("orchestration.agent_chain.orchestrator.build_agent_invocation_directive")
    @patch("orchestration.agent_chain.orchestrator.build_task_tool_directive")
    @patch("orchestration.agent_chain.orchestrator.verify_memory_file_exists")
    def test_different_agents_each_get_learnings(
        self, mock_verify, mock_task_directive, mock_agent_directive, mock_config,
        simple_flow, tmp_path, monkeypatch
    ):
        """Each different agent should get learnings directive on first invocation."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}
        mock_agent_directive.return_value = "agent directive"
        mock_task_directive.return_value = "task directive"
        mock_verify.return_value = True

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        # Start flow (clarification - first time)
        orchestrator.start_flow()

        first_call_kwargs = mock_agent_directive.call_args[1]
        assert first_call_kwargs["include_learnings_directive"] is True
        assert first_call_kwargs["agent_name"] == "clarification"

        # Advance to research (first time for this agent)
        mock_agent_directive.reset_mock()
        orchestrator.get_next_directive("clarification")

        second_call_kwargs = mock_agent_directive.call_args[1]
        assert second_call_kwargs["include_learnings_directive"] is True
        assert second_call_kwargs["agent_name"] == "research"

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_learnings_marked_before_directive_built(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """Learnings should be marked BEFORE directive is built (crash safety)."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        orchestrator.start_flow()

        # After start_flow, state should already have clarification marked
        assert "clarification" in orchestrator.state.learnings_injected_for

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_learnings_persisted_to_disk(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """Learnings state should be saved to disk immediately."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        orchestrator.start_flow()

        # Load state from disk and verify
        loaded_state = ChainState.load("test-123")
        assert loaded_state is not None
        assert "clarification" in loaded_state.learnings_injected_for


class TestChainOrchestratorBasic:
    """Basic tests for ChainOrchestrator functionality."""

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_start_flow_returns_directive(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """start_flow should return a directive string."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        directive = orchestrator.start_flow()

        assert isinstance(directive, str)
        assert len(directive) > 0
        assert "MANDATORY" in directive

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_get_current_step(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """get_current_step should return the current step."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        step = orchestrator.get_current_step()

        assert step is not None
        assert step.agent_name == "clarification"

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_is_flow_complete_initially_false(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """is_flow_complete should be False initially."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = ChainOrchestrator(
            flow=simple_flow,
            task_id="test-123",
        )

        assert orchestrator.is_flow_complete() is False


class TestLoadOrchestrator:
    """Tests for load_orchestrator function."""

    @patch("orchestration.agent_chain.orchestrator.get_agent_config")
    def test_creates_orchestrator(
        self, mock_config, simple_flow, tmp_path, monkeypatch
    ):
        """load_orchestrator should create an orchestrator."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )
        mock_config.return_value = {"model": "sonnet"}

        orchestrator = load_orchestrator(
            task_id="test-123",
            flow=simple_flow,
        )

        assert isinstance(orchestrator, ChainOrchestrator)
        assert orchestrator.task_id == "test-123"
