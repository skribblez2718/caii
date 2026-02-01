"""
Scaffold-Docs Flows Unit Tests

Tests for flow definitions and flow retrieval.
"""

import pytest


@pytest.mark.unit
class TestScaffoldDocsFlows:
    """Tests for scaffold-docs flow definitions."""

    def test_scaffold_flow_exists(self):
        """SCAFFOLD_FLOW should be defined."""
        from orchestration.skills.scaffold_docs.flows import SCAFFOLD_FLOW

        assert SCAFFOLD_FLOW is not None
        assert SCAFFOLD_FLOW.flow_id == "scaffold-docs-scaffold"

    def test_update_flow_exists(self):
        """UPDATE_FLOW should be defined."""
        from orchestration.skills.scaffold_docs.flows import UPDATE_FLOW

        assert UPDATE_FLOW is not None
        assert UPDATE_FLOW.flow_id == "scaffold-docs-update"

    def test_scaffold_flow_agents(self):
        """SCAFFOLD_FLOW should have correct agents in order."""
        from orchestration.skills.scaffold_docs.flows import SCAFFOLD_FLOW

        agent_names = [step.agent_name for step in SCAFFOLD_FLOW.steps]

        assert agent_names == ["clarification", "analysis", "synthesis", "validation"]

    def test_update_flow_agents(self):
        """UPDATE_FLOW should skip clarification."""
        from orchestration.skills.scaffold_docs.flows import UPDATE_FLOW

        agent_names = [step.agent_name for step in UPDATE_FLOW.steps]

        assert agent_names == ["analysis", "synthesis", "validation"]
        assert "clarification" not in agent_names

    def test_get_flow_for_scaffold_mode(self):
        """get_flow_for_mode should return SCAFFOLD_FLOW for scaffold."""
        from orchestration.skills.scaffold_docs.flows import (
            get_flow_for_mode,
            SCAFFOLD_FLOW,
        )

        flow = get_flow_for_mode("scaffold")

        assert flow == SCAFFOLD_FLOW

    def test_get_flow_for_update_mode(self):
        """get_flow_for_mode should return UPDATE_FLOW for update."""
        from orchestration.skills.scaffold_docs.flows import (
            get_flow_for_mode,
            UPDATE_FLOW,
        )

        flow = get_flow_for_mode("update")

        assert flow == UPDATE_FLOW

    def test_get_flow_for_invalid_mode_raises(self):
        """get_flow_for_mode should raise for invalid mode."""
        from orchestration.skills.scaffold_docs.flows import get_flow_for_mode

        with pytest.raises(ValueError) as exc_info:
            get_flow_for_mode("invalid")  # type: ignore

        assert "Invalid mode" in str(exc_info.value)

    def test_scaffold_flow_content_files(self):
        """SCAFFOLD_FLOW steps should reference correct content files."""
        from orchestration.skills.scaffold_docs.flows import SCAFFOLD_FLOW

        for step in SCAFFOLD_FLOW.steps:
            assert step.content_file.startswith("scaffold/")
            assert step.content_file.endswith(".md")

    def test_update_flow_content_files(self):
        """UPDATE_FLOW steps should reference correct content files."""
        from orchestration.skills.scaffold_docs.flows import UPDATE_FLOW

        for step in UPDATE_FLOW.steps:
            assert step.content_file.startswith("update/")
            assert step.content_file.endswith(".md")

    def test_flow_source_is_skill(self):
        """Both flows should have source='skill'."""
        from orchestration.skills.scaffold_docs.flows import (
            SCAFFOLD_FLOW,
            UPDATE_FLOW,
        )

        assert SCAFFOLD_FLOW.source == "skill"
        assert UPDATE_FLOW.source == "skill"

    def test_flow_predecessors_chain(self):
        """Flow steps should have correct predecessor chains."""
        from orchestration.skills.scaffold_docs.flows import SCAFFOLD_FLOW

        # Analysis should depend on clarification
        analysis_step = next(
            s for s in SCAFFOLD_FLOW.steps if s.agent_name == "analysis"
        )
        assert "clarification" in analysis_step.predecessors

        # Synthesis should depend on multiple predecessors
        synthesis_step = next(
            s for s in SCAFFOLD_FLOW.steps if s.agent_name == "synthesis"
        )
        assert "clarification" in synthesis_step.predecessors
        assert "analysis" in synthesis_step.predecessors

        # Validation should see all prior work
        validation_step = next(
            s for s in SCAFFOLD_FLOW.steps if s.agent_name == "validation"
        )
        assert len(validation_step.predecessors) >= 2


@pytest.mark.unit
class TestFlowStepProperties:
    """Tests for individual flow step properties."""

    def test_clarification_is_first_in_scaffold(self):
        """Clarification should be first step in scaffold flow."""
        from orchestration.skills.scaffold_docs.flows import SCAFFOLD_FLOW

        first_step = SCAFFOLD_FLOW.steps[0]
        assert first_step.agent_name == "clarification"
        assert first_step.predecessors == ()

    def test_analysis_is_first_in_update(self):
        """Analysis should be first step in update flow."""
        from orchestration.skills.scaffold_docs.flows import UPDATE_FLOW

        first_step = UPDATE_FLOW.steps[0]
        assert first_step.agent_name == "analysis"
        assert first_step.predecessors == ()

    def test_validation_is_last_in_both_flows(self):
        """Validation should be last step in both flows."""
        from orchestration.skills.scaffold_docs.flows import (
            SCAFFOLD_FLOW,
            UPDATE_FLOW,
        )

        assert SCAFFOLD_FLOW.steps[-1].agent_name == "validation"
        assert UPDATE_FLOW.steps[-1].agent_name == "validation"
