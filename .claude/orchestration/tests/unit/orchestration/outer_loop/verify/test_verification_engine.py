"""
Unit tests for outer_loop/verify/verification_engine.py

Tests the 4-layer verification engine:
- Layer 1 (Objective): 50% weight - Automatable checks
- Layer 2 (Heuristic): 30% weight - Pattern-based rules
- Layer 3 (Semantic): 20% weight - LLM-judged
- Layer 4 (User): Final confirmation (not in scoring)
"""

from typing import Dict, Any, List
from unittest.mock import MagicMock

import pytest

from orchestration.state.algorithm_state import (
    IdealState,
    SuccessCriterion,
    AntiCriterion,
    SuccessMetric,
    VerificationResult,
)


@pytest.fixture
def sample_ideal_state() -> IdealState:
    """Create a sample IdealState for testing."""
    return IdealState(
        task_id="test-task-123",
        task_type="CODING",
        objective="Build REST API endpoint",
        euphoric_surprise="Blazing fast with automatic caching",
        success_criteria=[
            SuccessCriterion(
                id="SC1",
                description="API returns valid JSON",
                verification_method="automated",
                weight=1.0,
            ),
            SuccessCriterion(
                id="SC2",
                description="Tests pass",
                verification_method="automated",
                weight=1.0,
            ),
        ],
        anti_criteria=[
            AntiCriterion(
                id="AC1",
                description="No hardcoded credentials",
                severity="critical",
            ),
        ],
        success_metrics=[
            SuccessMetric(
                id="M1",
                name="test_coverage",
                target_value=80,
                unit="%",
            ),
        ],
        completeness_score=0.95,
    )


@pytest.fixture
def sample_phase_outputs() -> Dict[str, Any]:
    """Sample phase outputs for verification."""
    return {
        "BUILD": {
            "files_created": ["src/api.py", "tests/test_api.py"],
            "test_results": {"passed": 10, "failed": 0},
        },
        "EXECUTE": {
            "status": "completed",
            "outputs": ["API endpoint running on port 8080"],
        },
    }


class TestVerificationEngineImport:
    """Tests for verification engine module import."""

    @pytest.mark.unit
    def test_verification_engine_exists(self):
        """VerificationEngine should be importable."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        assert VerificationEngine is not None

    @pytest.mark.unit
    def test_verification_engine_verify_method(self):
        """VerificationEngine should have verify() method."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        assert hasattr(VerificationEngine, "verify")


class TestObjectiveLayer:
    """Tests for Layer 1: Objective (50% weight)."""

    @pytest.mark.unit
    def test_objective_layer_weight_is_fifty_percent(self):
        """Objective layer should have 50% weight."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        assert engine.OBJECTIVE_WEIGHT == 0.5

    @pytest.mark.unit
    def test_objective_layer_syntax_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Objective layer should verify syntax validation."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_objective_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert 0.0 <= score <= 1.0

    @pytest.mark.unit
    def test_objective_layer_test_pass_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Objective layer should check if tests pass."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        # All tests passed in sample_phase_outputs
        score = engine._evaluate_objective_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert score > 0.5  # Tests passing should contribute positively

    @pytest.mark.unit
    def test_objective_layer_format_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Objective layer should verify format compliance."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_objective_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert isinstance(score, float)

    @pytest.mark.unit
    def test_objective_layer_all_pass_returns_one(self, sample_ideal_state):
        """When all objective checks pass, should return 1.0."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        perfect_outputs = {
            "BUILD": {"test_results": {"passed": 10, "failed": 0}},
            "EXECUTE": {"status": "completed"},
        }
        engine = VerificationEngine()
        score = engine._evaluate_objective_layer(sample_ideal_state, perfect_outputs)
        assert score == 1.0

    @pytest.mark.unit
    def test_objective_layer_partial_pass(self, sample_ideal_state):
        """When some checks fail, should return proportional score."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        partial_outputs = {
            "BUILD": {"test_results": {"passed": 5, "failed": 5}},
            "EXECUTE": {"status": "completed"},
        }
        engine = VerificationEngine()
        score = engine._evaluate_objective_layer(sample_ideal_state, partial_outputs)
        assert 0.0 < score < 1.0


class TestHeuristicLayer:
    """Tests for Layer 2: Heuristic (30% weight)."""

    @pytest.mark.unit
    def test_heuristic_layer_weight_is_thirty_percent(self):
        """Heuristic layer should have 30% weight."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        assert engine.HEURISTIC_WEIGHT == 0.3

    @pytest.mark.unit
    def test_heuristic_layer_complexity_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Heuristic layer should analyze code complexity."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_heuristic_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert 0.0 <= score <= 1.0

    @pytest.mark.unit
    def test_heuristic_layer_style_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Heuristic layer should verify style guide compliance."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_heuristic_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert isinstance(score, float)

    @pytest.mark.unit
    def test_heuristic_layer_pattern_check(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Heuristic layer should verify pattern matching."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_heuristic_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert score >= 0.0


class TestSemanticLayer:
    """Tests for Layer 3: Semantic (20% weight)."""

    @pytest.mark.unit
    def test_semantic_layer_weight_is_twenty_percent(self):
        """Semantic layer should have 20% weight."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        assert engine.SEMANTIC_WEIGHT == 0.2

    @pytest.mark.unit
    def test_semantic_layer_returns_score(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Semantic layer should return a 0-1 score."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        score = engine._evaluate_semantic_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert 0.0 <= score <= 1.0

    @pytest.mark.unit
    def test_semantic_layer_intent_match(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """Semantic layer should evaluate intent alignment."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        # Should evaluate if output matches stated objective
        score = engine._evaluate_semantic_layer(
            sample_ideal_state, sample_phase_outputs
        )
        assert isinstance(score, float)


class TestVerificationEngineOverall:
    """Tests for overall VerificationEngine behavior."""

    @pytest.mark.unit
    def test_weighted_score_calculation(self, sample_ideal_state, sample_phase_outputs):
        """Verify() should calculate weighted average of all layers."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, sample_phase_outputs, iteration=1)

        assert isinstance(result, VerificationResult)
        # Weighted: objective_score * 0.5 + heuristic_score * 0.3 + semantic_score * 0.2
        expected_overall = (
            result.objective_score * 0.5
            + result.heuristic_score * 0.3
            + result.semantic_score * 0.2
        )
        assert abs(result.overall_score - expected_overall) < 0.01

    @pytest.mark.unit
    def test_status_verified_when_score_high(self, sample_ideal_state):
        """Score >= 0.9 should result in VERIFIED status."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        perfect_outputs = {
            "BUILD": {"test_results": {"passed": 10, "failed": 0}},
            "EXECUTE": {"status": "completed", "all_criteria_met": True},
        }
        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, perfect_outputs, iteration=1)

        if result.overall_score >= 0.9:
            assert result.status == "VERIFIED"

    @pytest.mark.unit
    def test_status_gaps_when_score_medium(self, sample_ideal_state):
        """Score between 0.6-0.9 should result in GAPS_IDENTIFIED status."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        partial_outputs = {
            "BUILD": {"test_results": {"passed": 7, "failed": 3}},
            "EXECUTE": {"status": "completed"},
        }
        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, partial_outputs, iteration=1)

        if 0.6 <= result.overall_score < 0.9:
            assert result.status == "GAPS_IDENTIFIED"

    @pytest.mark.unit
    def test_status_critical_when_score_low(self, sample_ideal_state):
        """Score < 0.6 should result in CRITICAL_FAILURE status."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        bad_outputs = {
            "BUILD": {"test_results": {"passed": 2, "failed": 8}},
            "EXECUTE": {"status": "failed"},
        }
        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, bad_outputs, iteration=1)

        if result.overall_score < 0.6:
            assert result.status == "CRITICAL_FAILURE"

    @pytest.mark.unit
    def test_anti_criteria_violation_forces_critical_failure(self):
        """Anti-criteria violation should force CRITICAL_FAILURE regardless of score."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        ideal_state = IdealState(
            task_id="test",
            task_type="CODING",
            objective="Build API",
            euphoric_surprise="Fast",
            anti_criteria=[
                AntiCriterion(
                    id="AC1",
                    description="No hardcoded credentials",
                    severity="critical",
                ),
            ],
        )
        # Outputs contain anti-criteria violation
        outputs_with_violation = {
            "BUILD": {
                "test_results": {"passed": 10, "failed": 0},
                "anti_criteria_violations": ["AC1"],
            },
        }
        engine = VerificationEngine()
        result = engine.verify(ideal_state, outputs_with_violation, iteration=1)

        assert result.status == "CRITICAL_FAILURE"

    @pytest.mark.unit
    def test_verify_returns_verification_result(
        self, sample_ideal_state, sample_phase_outputs
    ):
        """verify() should return a VerificationResult instance."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, sample_phase_outputs, iteration=1)

        assert isinstance(result, VerificationResult)
        assert hasattr(result, "iteration")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "status")
        assert hasattr(result, "objective_score")
        assert hasattr(result, "heuristic_score")
        assert hasattr(result, "semantic_score")
        assert hasattr(result, "overall_score")
        assert hasattr(result, "gaps")
        assert hasattr(result, "recommendations")

    @pytest.mark.unit
    def test_verify_includes_iteration(self, sample_ideal_state, sample_phase_outputs):
        """VerificationResult should include the iteration number."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, sample_phase_outputs, iteration=2)

        assert result.iteration == 2

    @pytest.mark.unit
    def test_verify_handles_missing_ideal_state(self, sample_phase_outputs):
        """verify() should handle None ideal_state gracefully."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        with pytest.raises((ValueError, TypeError)):
            engine.verify(None, sample_phase_outputs, iteration=1)

    @pytest.mark.unit
    def test_verify_handles_empty_phase_outputs(self, sample_ideal_state):
        """verify() should handle empty phase_outputs."""
        from orchestration.outer_loop.verify.verification_engine import (
            VerificationEngine,
        )

        engine = VerificationEngine()
        result = engine.verify(sample_ideal_state, {}, iteration=1)

        # Should still produce a result, likely with low scores
        assert isinstance(result, VerificationResult)
        assert result.overall_score < 0.5  # Empty outputs shouldn't score well
