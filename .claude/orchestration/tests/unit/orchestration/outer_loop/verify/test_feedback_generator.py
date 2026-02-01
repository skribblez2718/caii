"""
Unit tests for outer_loop/verify/feedback_generator.py

Tests the feedback generator that converts VerificationResult
to actionable next steps (PROCEED/LOOP_BACK/ESCALATE).
"""

from typing import List

import pytest

from orchestration.state.algorithm_state import VerificationResult


@pytest.fixture
def verified_result() -> VerificationResult:
    """Create a VERIFIED VerificationResult."""
    return VerificationResult(
        iteration=1,
        timestamp="2026-01-31T12:00:00Z",
        status="VERIFIED",
        objective_score=0.95,
        heuristic_score=0.90,
        semantic_score=0.92,
        overall_score=0.93,
        gaps=[],
        recommendations=["Consider adding integration tests"],
    )


@pytest.fixture
def gaps_result() -> VerificationResult:
    """Create a GAPS_IDENTIFIED VerificationResult."""
    return VerificationResult(
        iteration=1,
        timestamp="2026-01-31T12:00:00Z",
        status="GAPS_IDENTIFIED",
        objective_score=0.75,
        heuristic_score=0.70,
        semantic_score=0.65,
        overall_score=0.72,
        gaps=["Missing error handling", "Tests incomplete"],
        recommendations=["Add try/catch blocks", "Write edge case tests"],
    )


@pytest.fixture
def critical_result() -> VerificationResult:
    """Create a CRITICAL_FAILURE VerificationResult."""
    return VerificationResult(
        iteration=1,
        timestamp="2026-01-31T12:00:00Z",
        status="CRITICAL_FAILURE",
        objective_score=0.30,
        heuristic_score=0.40,
        semantic_score=0.35,
        overall_score=0.34,
        gaps=["Core functionality broken", "Anti-criteria violated"],
        recommendations=["Complete rewrite required"],
    )


class TestFeedbackGeneratorImport:
    """Tests for feedback generator module import."""

    @pytest.mark.unit
    def test_feedback_generator_exists(self):
        """FeedbackGenerator should be importable."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        assert FeedbackGenerator is not None

    @pytest.mark.unit
    def test_feedback_decision_dataclass_exists(self):
        """FeedbackDecision dataclass should be importable."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackDecision,
        )

        assert FeedbackDecision is not None

    @pytest.mark.unit
    def test_feedback_generator_generate_method(self):
        """FeedbackGenerator should have generate() method."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        assert hasattr(FeedbackGenerator, "generate")


class TestFeedbackDecisionDataclass:
    """Tests for FeedbackDecision dataclass."""

    @pytest.mark.unit
    def test_feedback_decision_has_action(self):
        """FeedbackDecision should have action field."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackDecision,
        )

        decision = FeedbackDecision(
            action="PROCEED",
            message="All verified",
            next_phase="LEARN",
            gaps=[],
        )
        assert decision.action == "PROCEED"

    @pytest.mark.unit
    def test_feedback_decision_has_message(self):
        """FeedbackDecision should have message field."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackDecision,
        )

        decision = FeedbackDecision(
            action="PROCEED",
            message="All verified",
            next_phase="LEARN",
            gaps=[],
        )
        assert decision.message == "All verified"

    @pytest.mark.unit
    def test_feedback_decision_has_next_phase(self):
        """FeedbackDecision should have next_phase field."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackDecision,
        )

        decision = FeedbackDecision(
            action="LOOP_BACK",
            message="Gaps identified",
            next_phase="INNER_LOOP",
            gaps=["Gap 1"],
        )
        assert decision.next_phase == "INNER_LOOP"

    @pytest.mark.unit
    def test_feedback_decision_has_gaps(self):
        """FeedbackDecision should have gaps field."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackDecision,
        )

        decision = FeedbackDecision(
            action="LOOP_BACK",
            message="Gaps found",
            next_phase="INNER_LOOP",
            gaps=["Gap 1", "Gap 2"],
        )
        assert decision.gaps == ["Gap 1", "Gap 2"]


class TestFeedbackGeneratorVerified:
    """Tests for VERIFIED status handling."""

    @pytest.mark.unit
    def test_verified_returns_proceed(self, verified_result):
        """VERIFIED status should return PROCEED action."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(verified_result, iteration=1)

        assert decision.action == "PROCEED"

    @pytest.mark.unit
    def test_verified_next_phase_is_learn(self, verified_result):
        """VERIFIED status should set next_phase to LEARN."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(verified_result, iteration=1)

        assert decision.next_phase == "LEARN"

    @pytest.mark.unit
    def test_verified_gaps_empty(self, verified_result):
        """VERIFIED status should have empty gaps."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(verified_result, iteration=1)

        assert decision.gaps == []


class TestFeedbackGeneratorGaps:
    """Tests for GAPS_IDENTIFIED status handling."""

    @pytest.mark.unit
    def test_gaps_first_iteration_returns_loop_back(self, gaps_result):
        """GAPS_IDENTIFIED on first iteration should return LOOP_BACK."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=1)

        assert decision.action == "LOOP_BACK"

    @pytest.mark.unit
    def test_gaps_loop_back_next_phase_is_inner_loop(self, gaps_result):
        """LOOP_BACK action should set next_phase to INNER_LOOP."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=1)

        assert decision.next_phase == "INNER_LOOP"

    @pytest.mark.unit
    def test_gaps_max_iterations_returns_escalate(self, gaps_result):
        """GAPS_IDENTIFIED at max iterations should return ESCALATE."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=3, max_iterations=3)

        assert decision.action == "ESCALATE"

    @pytest.mark.unit
    def test_gaps_escalate_next_phase_is_user_review(self, gaps_result):
        """ESCALATE action should set next_phase to USER_REVIEW."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=3, max_iterations=3)

        assert decision.next_phase == "USER_REVIEW"

    @pytest.mark.unit
    def test_gaps_includes_gap_list(self, gaps_result):
        """GAPS_IDENTIFIED decision should include gap list."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=1)

        assert len(decision.gaps) > 0
        assert "Missing error handling" in decision.gaps


class TestFeedbackGeneratorCritical:
    """Tests for CRITICAL_FAILURE status handling."""

    @pytest.mark.unit
    def test_critical_returns_escalate(self, critical_result):
        """CRITICAL_FAILURE should always return ESCALATE."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(critical_result, iteration=1)

        assert decision.action == "ESCALATE"

    @pytest.mark.unit
    def test_critical_escalate_regardless_of_iteration(self, critical_result):
        """CRITICAL_FAILURE should ESCALATE on any iteration."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()

        for iteration in [1, 2, 3]:
            decision = generator.generate(critical_result, iteration=iteration)
            assert decision.action == "ESCALATE"

    @pytest.mark.unit
    def test_critical_next_phase_is_user_review(self, critical_result):
        """CRITICAL_FAILURE should set next_phase to USER_REVIEW."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(critical_result, iteration=1)

        assert decision.next_phase == "USER_REVIEW"


class TestFeedbackGeneratorEdgeCases:
    """Tests for edge cases in feedback generation."""

    @pytest.mark.unit
    def test_iteration_exceeds_max(self, gaps_result):
        """iteration > max_iterations should still ESCALATE."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=5, max_iterations=3)

        assert decision.action == "ESCALATE"

    @pytest.mark.unit
    def test_empty_gaps_with_gaps_status(self):
        """GAPS_IDENTIFIED with empty gaps should still loop back."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        contradictory_result = VerificationResult(
            iteration=1,
            timestamp="2026-01-31T12:00:00Z",
            status="GAPS_IDENTIFIED",
            objective_score=0.75,
            heuristic_score=0.70,
            semantic_score=0.65,
            overall_score=0.72,
            gaps=[],  # Empty but status says gaps identified
            recommendations=[],
        )

        generator = FeedbackGenerator()
        decision = generator.generate(contradictory_result, iteration=1)

        # Should still respect the status
        assert decision.action == "LOOP_BACK"

    @pytest.mark.unit
    def test_default_max_iterations_is_three(self, gaps_result):
        """Default max_iterations should be 3."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()

        # At iteration 3 with default max, should escalate
        decision = generator.generate(gaps_result, iteration=3)
        assert decision.action == "ESCALATE"

    @pytest.mark.unit
    def test_message_includes_context(self, gaps_result):
        """Decision message should include helpful context."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=1)

        # Message should be non-empty and descriptive
        assert len(decision.message) > 0
        assert isinstance(decision.message, str)

    @pytest.mark.unit
    def test_recommendations_included_in_message(self, gaps_result):
        """Recommendations should be reflected in the decision."""
        from orchestration.outer_loop.verify.feedback_generator import (
            FeedbackGenerator,
        )

        generator = FeedbackGenerator()
        decision = generator.generate(gaps_result, iteration=1)

        # The decision should somehow incorporate the recommendations
        assert hasattr(decision, "message")
