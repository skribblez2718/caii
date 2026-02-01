"""
Unit tests for flow_registry.py

Tests the central registry for agent flow lookup by ID.
"""

import pytest

# ============================================================================
# get_flow Tests
# ============================================================================


@pytest.mark.unit
class TestGetFlow:
    """Tests for get_flow function."""

    def test_get_flow_returns_tdd_red_flow(self):
        """get_flow should return TDD RED flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.skills.perform_tdd.flows import TDD_RED_FLOW

        result = get_flow("perform-tdd-red")

        assert result is not None
        assert result.flow_id == "perform-tdd-red"
        assert result == TDD_RED_FLOW

    def test_get_flow_returns_tdd_green_flow(self):
        """get_flow should return TDD GREEN flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.skills.perform_tdd.flows import TDD_GREEN_FLOW

        result = get_flow("perform-tdd-green")

        assert result is not None
        assert result.flow_id == "perform-tdd-green"
        assert result == TDD_GREEN_FLOW

    def test_get_flow_returns_tdd_refactor_flow(self):
        """get_flow should return TDD REFACTOR flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.skills.perform_tdd.flows import TDD_REFACTOR_FLOW

        result = get_flow("perform-tdd-refactor")

        assert result is not None
        assert result.flow_id == "perform-tdd-refactor"
        assert result == TDD_REFACTOR_FLOW

    def test_get_flow_returns_tdd_doc_flow(self):
        """get_flow should return TDD DOC flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.skills.perform_tdd.flows import TDD_DOC_FLOW

        result = get_flow("perform-tdd-doc")

        assert result is not None
        assert result.flow_id == "perform-tdd-doc"
        assert result == TDD_DOC_FLOW

    def test_get_flow_returns_decompose_flow(self):
        """get_flow should return DECOMPOSE flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.decompose.flows import DECOMPOSE_FLOW

        result = get_flow("decompose-protocol")

        assert result is not None
        assert result.flow_id == "decompose-protocol"
        assert result == DECOMPOSE_FLOW

    def test_get_flow_returns_aggregation_flow(self):
        """get_flow should return AGGREGATION flow by ID."""
        from orchestration.flow_registry import get_flow
        from orchestration.decompose.flows import AGGREGATION_FLOW

        result = get_flow("decompose-aggregation")

        assert result is not None
        assert result.flow_id == "decompose-aggregation"
        assert result == AGGREGATION_FLOW

    def test_get_flow_returns_none_for_unknown_id(self):
        """get_flow should return None for unknown flow ID."""
        from orchestration.flow_registry import get_flow

        result = get_flow("unknown-flow-id")

        assert result is None

    def test_get_flow_returns_none_for_empty_id(self):
        """get_flow should return None for empty string ID."""
        from orchestration.flow_registry import get_flow

        result = get_flow("")

        assert result is None


# ============================================================================
# register_flow Tests
# ============================================================================


@pytest.mark.unit
class TestRegisterFlow:
    """Tests for register_flow function."""

    def test_register_flow_adds_new_flow(self):
        """register_flow should add a new flow to registry."""
        from orchestration.flow_registry import get_flow, register_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        # Create a custom flow
        custom_flow = AgentFlow(
            flow_id="custom-test-flow",
            name="Custom Test Flow",
            source="dynamic",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        # Register it
        register_flow(custom_flow)

        # Should be retrievable
        result = get_flow("custom-test-flow")
        assert result is not None
        assert result.flow_id == "custom-test-flow"
        assert result == custom_flow

    def test_register_flow_overwrites_existing(self):
        """register_flow should overwrite existing flow with same ID."""
        from orchestration.flow_registry import get_flow, register_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        # Create two flows with same ID but different names
        flow1 = AgentFlow(
            flow_id="overwrite-test",
            name="Original Flow",
            source="dynamic",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        flow2 = AgentFlow(
            flow_id="overwrite-test",
            name="Replacement Flow",
            source="dynamic",
            steps=(
                FlowStep(
                    agent_name="generation",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        register_flow(flow1)
        register_flow(flow2)

        result = get_flow("overwrite-test")
        assert result is not None
        assert result.name == "Replacement Flow"


# ============================================================================
# list_flows Tests
# ============================================================================


@pytest.mark.unit
class TestListFlows:
    """Tests for list_flows function."""

    def test_list_flows_includes_all_tdd_flows(self):
        """list_flows should include all TDD flow IDs."""
        from orchestration.flow_registry import list_flows

        flow_ids = list_flows()

        assert "perform-tdd-red" in flow_ids
        assert "perform-tdd-green" in flow_ids
        assert "perform-tdd-refactor" in flow_ids
        assert "perform-tdd-doc" in flow_ids

    def test_list_flows_includes_decompose_flows(self):
        """list_flows should include DECOMPOSE flow IDs."""
        from orchestration.flow_registry import list_flows

        flow_ids = list_flows()

        assert "decompose-protocol" in flow_ids
        assert "decompose-aggregation" in flow_ids

    def test_list_flows_returns_list(self):
        """list_flows should return a list."""
        from orchestration.flow_registry import list_flows

        flow_ids = list_flows()

        assert isinstance(flow_ids, list)

    def test_list_flows_includes_registered_flows(self):
        """list_flows should include dynamically registered flows."""
        from orchestration.flow_registry import list_flows, register_flow
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        custom_flow = AgentFlow(
            flow_id="list-test-custom",
            name="List Test Custom",
            source="dynamic",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        register_flow(custom_flow)

        flow_ids = list_flows()
        assert "list-test-custom" in flow_ids


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestFlowRegistryInitialization:
    """Tests for flow registry initialization behavior."""

    def test_registry_initializes_on_first_get_flow(self):
        """Registry should initialize lazily on first get_flow call."""
        # This test verifies the lazy initialization pattern
        # The registry should not fail if imports succeed
        from orchestration.flow_registry import get_flow

        # Should not raise
        result = get_flow("perform-tdd-red")
        assert result is not None

    def test_registry_initializes_on_first_list_flows(self):
        """Registry should initialize lazily on first list_flows call."""
        from orchestration.flow_registry import list_flows

        # Should not raise
        result = list_flows()
        assert len(result) >= 6  # At least TDD + DECOMPOSE flows

    def test_multiple_get_flow_calls_work(self):
        """Multiple get_flow calls should work correctly."""
        from orchestration.flow_registry import get_flow

        # Get multiple flows
        red = get_flow("perform-tdd-red")
        green = get_flow("perform-tdd-green")
        decompose = get_flow("decompose-protocol")

        assert red is not None
        assert green is not None
        assert decompose is not None
        assert red.flow_id != green.flow_id
