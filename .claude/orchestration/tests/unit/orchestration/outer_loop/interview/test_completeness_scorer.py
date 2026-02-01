"""
Completeness Scorer Unit Tests

Tests for IDEAL STATE completeness evaluation.
"""

import pytest


@pytest.mark.unit
class TestCompletenessWeights:
    """Tests for completeness weight configuration."""

    def test_weights_sum_to_one(self):
        """Weights should sum to 1.0."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            COMPLETENESS_WEIGHTS,
        )

        total = sum(COMPLETENESS_WEIGHTS.values())

        assert abs(total - 1.0) < 0.001

    def test_all_dimensions_have_weights(self):
        """All required dimensions should have weights."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            COMPLETENESS_WEIGHTS,
        )

        required = [
            "criteria_clarity",
            "metric_precision",
            "verification_feasibility",
            "anti_criteria_coverage",
            "exit_clarity",
            "intent_alignment",
        ]

        for dim in required:
            assert dim in COMPLETENESS_WEIGHTS

    def test_threshold_is_95_percent(self):
        """Completeness threshold should be 0.95."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            COMPLETENESS_THRESHOLD,
        )

        assert COMPLETENESS_THRESHOLD == 0.95

    def test_max_iterations_is_5(self):
        """Max interview iterations should be 5."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            MAX_INTERVIEW_ITERATIONS,
        )

        assert MAX_INTERVIEW_ITERATIONS == 5


@pytest.mark.unit
class TestScoreCriteriaClarity:
    """Tests for criteria clarity scoring."""

    def test_no_criteria_returns_zero(self):
        """No criteria should return 0."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_criteria_clarity,
        )

        result = score_criteria_clarity({"success_criteria": []})

        assert result == 0.0

    def test_one_criterion_returns_half(self):
        """One criterion should return 0.5 max."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_criteria_clarity,
        )

        ideal = {
            "success_criteria": [
                {"description": "Test", "verification_method": "pytest"}
            ]
        }

        result = score_criteria_clarity(ideal)

        assert result == 0.5

    def test_two_complete_criteria_returns_one(self):
        """Two complete criteria should return 1.0."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_criteria_clarity,
        )

        ideal = {
            "success_criteria": [
                {"description": "Test 1", "verification_method": "method 1"},
                {"description": "Test 2", "verification_method": "method 2"},
            ]
        }

        result = score_criteria_clarity(ideal)

        assert result == 1.0

    def test_partial_criteria(self):
        """Criteria without verification should get partial score."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_criteria_clarity,
        )

        ideal = {
            "success_criteria": [
                {"description": "Test 1"},  # No verification_method
                {"description": "Test 2", "verification_method": "method 2"},
            ]
        }

        result = score_criteria_clarity(ideal)

        # First: 0.5 (description only), Second: 1.0
        # Average: 0.75
        assert result == 0.75


@pytest.mark.unit
class TestScoreMetricPrecision:
    """Tests for metric precision scoring."""

    def test_no_metrics_partial_credit(self):
        """No metrics should get 0.3 partial credit."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_metric_precision,
        )

        result = score_metric_precision({"success_metrics": []})

        assert result == 0.3

    def test_complete_metric(self):
        """Complete metric should score 1.0."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_metric_precision,
        )

        ideal = {
            "success_metrics": [{"name": "Coverage", "target_value": 90, "unit": "%"}]
        }

        result = score_metric_precision(ideal)

        assert result == 1.0

    def test_partial_metric(self):
        """Metric without unit gets partial score."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            score_metric_precision,
        )

        ideal = {"success_metrics": [{"name": "Score", "target_value": 10}]}

        result = score_metric_precision(ideal)

        # 0.3 (name) + 0.5 (target_value) = 0.8
        assert result == 0.8


@pytest.mark.unit
class TestEvaluateCompleteness:
    """Tests for full completeness evaluation."""

    def test_none_ideal_state(self):
        """None ideal state should return 0 score."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            evaluate_completeness,
        )

        result = evaluate_completeness(None)

        assert result.overall_score == 0.0
        assert result.ready_to_proceed is False

    def test_empty_ideal_state(self):
        """Empty ideal state should have low score."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            evaluate_completeness,
        )

        result = evaluate_completeness({})

        assert result.overall_score < 0.5
        assert result.ready_to_proceed is False

    def test_complete_ideal_state(self):
        """Complete ideal state should pass threshold."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            evaluate_completeness,
        )

        ideal = {
            "objective": "Build an API",
            "euphoric_surprise": "Auto-generates docs",
            "success_criteria": [
                {"description": "Tests pass", "verification_method": "pytest"},
                {"description": "Lint clean", "verification_method": "pylint"},
            ],
            "success_metrics": [{"name": "Coverage", "target_value": 90, "unit": "%"}],
            "anti_criteria": [
                {"description": "No security vulns", "severity": "critical"}
            ],
            "exit_conditions": ["All tests pass", "Coverage ≥ 90%"],
            "verification_method": "4-layer",
        }

        result = evaluate_completeness(ideal)

        assert result.overall_score >= 0.95
        assert result.ready_to_proceed is True

    def test_returns_dimension_scores(self):
        """Result should include individual dimension scores."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            evaluate_completeness,
        )

        ideal = {"objective": "Test", "success_criteria": []}

        result = evaluate_completeness(ideal)

        assert "criteria_clarity" in result.dimension_scores
        assert "metric_precision" in result.dimension_scores
        assert "intent_alignment" in result.dimension_scores

    def test_identifies_missing_elements(self):
        """Result should identify what's missing."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            evaluate_completeness,
        )

        ideal = {"objective": "Test"}  # Missing most elements

        result = evaluate_completeness(ideal)

        assert len(result.missing_elements) > 0
        assert len(result.recommendations) > 0


@pytest.mark.unit
class TestCompletenessResult:
    """Tests for CompletenessResult dataclass."""

    def test_dataclass_fields(self):
        """CompletenessResult should have all required fields."""
        from orchestration.outer_loop.interview.completeness_scorer import (
            CompletenessResult,
        )

        result = CompletenessResult(
            overall_score=0.85,
            dimension_scores={"test": 0.8},
            missing_elements=["X"],
            ready_to_proceed=False,
            recommendations=["Add X"],
        )

        assert result.overall_score == 0.85
        assert result.dimension_scores == {"test": 0.8}
        assert result.missing_elements == ["X"]
        assert result.ready_to_proceed is False
        assert result.recommendations == ["Add X"]
