"""
INTERVIEW Flows Unit Tests

Tests for INTERVIEW agent flow definitions.
"""

import pytest


@pytest.mark.unit
class TestInterviewFlow:
    """Tests for INTERVIEW_FLOW definition."""

    def test_flow_exists(self):
        """INTERVIEW_FLOW should exist."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_FLOW

        assert INTERVIEW_FLOW is not None

    def test_flow_has_correct_id(self):
        """Flow should have expected ID."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_FLOW

        assert INTERVIEW_FLOW.flow_id == "outer-loop-interview"

    def test_flow_has_correct_name(self):
        """Flow should have expected name."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_FLOW

        assert INTERVIEW_FLOW.name == "INTERVIEW Phase"

    def test_flow_has_two_steps(self):
        """Initial flow should have clarification -> validation."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_FLOW

        assert len(INTERVIEW_FLOW.steps) == 2

    def test_flow_agent_sequence(self):
        """Agents should be in clarification -> validation order."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_FLOW

        agents = [step.agent_name for step in INTERVIEW_FLOW.steps]

        assert agents == ["clarification", "validation"]


@pytest.mark.unit
class TestInterviewRefinementFlow:
    """Tests for INTERVIEW_REFINEMENT_FLOW definition."""

    def test_refinement_flow_exists(self):
        """INTERVIEW_REFINEMENT_FLOW should exist."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_REFINEMENT_FLOW

        assert INTERVIEW_REFINEMENT_FLOW is not None

    def test_refinement_flow_has_three_steps(self):
        """Refinement flow should have analysis -> clarification -> validation."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_REFINEMENT_FLOW

        assert len(INTERVIEW_REFINEMENT_FLOW.steps) == 3

    def test_refinement_flow_agent_sequence(self):
        """Refinement agents should be in correct order."""
        from orchestration.outer_loop.interview.flows import INTERVIEW_REFINEMENT_FLOW

        agents = [step.agent_name for step in INTERVIEW_REFINEMENT_FLOW.steps]

        assert agents == ["analysis", "clarification", "validation"]


@pytest.mark.unit
class TestGetInterviewFlow:
    """Tests for get_interview_flow function."""

    def test_iteration_0_returns_initial_flow(self):
        """Iteration 0 should return initial flow."""
        from orchestration.outer_loop.interview.flows import (
            INTERVIEW_FLOW,
            get_interview_flow,
        )

        result = get_interview_flow(0)

        assert result == INTERVIEW_FLOW

    def test_iteration_1_returns_refinement_flow(self):
        """Iteration > 0 should return refinement flow."""
        from orchestration.outer_loop.interview.flows import (
            INTERVIEW_REFINEMENT_FLOW,
            get_interview_flow,
        )

        result = get_interview_flow(1)

        assert result == INTERVIEW_REFINEMENT_FLOW

    def test_iteration_5_returns_refinement_flow(self):
        """High iteration should return refinement flow."""
        from orchestration.outer_loop.interview.flows import (
            INTERVIEW_REFINEMENT_FLOW,
            get_interview_flow,
        )

        result = get_interview_flow(5)

        assert result == INTERVIEW_REFINEMENT_FLOW
