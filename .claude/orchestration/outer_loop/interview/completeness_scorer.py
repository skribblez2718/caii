"""
Completeness Scorer

Evaluates IDEAL STATE completeness using weighted dimensions.
Target threshold: 95% for proceeding to INNER_LOOP.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CompletenessResult:
    """Result of completeness evaluation."""

    overall_score: float  # 0.0-1.0
    dimension_scores: Dict[str, float]  # Scores for each dimension
    missing_elements: List[str]  # What's needed for higher score
    ready_to_proceed: bool  # Whether 95% threshold met
    recommendations: List[str]  # Suggestions for improvement


# Completeness dimensions and their weights
COMPLETENESS_WEIGHTS = {
    "criteria_clarity": 0.25,  # Success criteria clearly defined
    "metric_precision": 0.20,  # Metrics are quantifiable
    "verification_feasibility": 0.20,  # Can be verified objectively
    "anti_criteria_coverage": 0.15,  # Anti-patterns identified
    "exit_clarity": 0.10,  # Exit conditions clear
    "intent_alignment": 0.10,  # User intent captured
}

# Threshold for proceeding to next phase
COMPLETENESS_THRESHOLD = 0.95

# Maximum iterations for INTERVIEW phase
MAX_INTERVIEW_ITERATIONS = 5


def score_criteria_clarity(ideal_state: dict) -> float:
    """
    Score clarity of success criteria.

    Checks:
    - At least 2 success criteria defined
    - Each criterion has description
    - Each criterion has verification method
    """
    criteria = ideal_state.get("success_criteria", [])

    if not criteria:
        return 0.0

    if len(criteria) < 2:
        return 0.5

    # Score each criterion
    criterion_scores = []
    for criterion in criteria:
        score = 0.0
        if criterion.get("description"):
            score += 0.5
        if criterion.get("verification_method"):
            score += 0.5
        criterion_scores.append(score)

    return sum(criterion_scores) / len(criterion_scores)


def score_metric_precision(ideal_state: dict) -> float:
    """
    Score precision of success metrics.

    Checks:
    - At least 1 metric defined
    - Metrics have target values
    - Metrics have units where applicable
    """
    metrics = ideal_state.get("success_metrics", [])

    if not metrics:
        return 0.3  # Partial credit for having criteria without metrics

    metric_scores = []
    for metric in metrics:
        score = 0.0
        if metric.get("name"):
            score += 0.3
        if metric.get("target_value") is not None:
            score += 0.5
        if metric.get("unit"):
            score += 0.2
        metric_scores.append(score)

    return sum(metric_scores) / len(metric_scores)


def score_verification_feasibility(ideal_state: dict) -> float:
    """
    Score feasibility of verification.

    Checks:
    - Verification method specified
    - Criteria can be objectively verified
    """
    verification_method = ideal_state.get("verification_method", "")
    criteria = ideal_state.get("success_criteria", [])

    if not verification_method:
        return 0.3

    base_score = 0.5  # Has a verification method

    # Check if criteria have verification methods
    if criteria:
        verifiable_count = sum(1 for c in criteria if c.get("verification_method"))
        base_score += 0.5 * (verifiable_count / len(criteria))

    return base_score


def score_anti_criteria_coverage(ideal_state: dict) -> float:
    """
    Score coverage of anti-criteria.

    Checks:
    - At least 1 anti-criterion defined
    - Anti-criteria cover critical failure modes
    """
    anti_criteria = ideal_state.get("anti_criteria", [])

    if not anti_criteria:
        return 0.5  # Partial credit - not always needed

    if len(anti_criteria) >= 2:
        return 1.0

    return 0.75


def score_exit_clarity(ideal_state: dict) -> float:
    """
    Score clarity of exit conditions.

    Checks:
    - At least 1 exit condition defined
    - Exit conditions are specific
    """
    exit_conditions = ideal_state.get("exit_conditions", [])

    if not exit_conditions:
        return 0.3

    if len(exit_conditions) >= 2:
        return 1.0

    return 0.7


def score_intent_alignment(ideal_state: dict) -> float:
    """
    Score alignment with user intent.

    Checks:
    - Objective clearly stated
    - Euphoric surprise captured
    """
    score = 0.0

    if ideal_state.get("objective"):
        score += 0.6

    if ideal_state.get("euphoric_surprise"):
        score += 0.4

    return score


def evaluate_completeness(ideal_state: Optional[dict]) -> CompletenessResult:
    """
    Evaluate completeness of IDEAL STATE.

    Args:
        ideal_state: Dictionary representation of IdealState

    Returns:
        CompletenessResult with scores and recommendations
    """
    if not ideal_state:
        return CompletenessResult(
            overall_score=0.0,
            dimension_scores={},
            missing_elements=["No IDEAL STATE defined"],
            ready_to_proceed=False,
            recommendations=["Define IDEAL STATE with objective and criteria"],
        )

    # Score each dimension
    dimension_scores = {
        "criteria_clarity": score_criteria_clarity(ideal_state),
        "metric_precision": score_metric_precision(ideal_state),
        "verification_feasibility": score_verification_feasibility(ideal_state),
        "anti_criteria_coverage": score_anti_criteria_coverage(ideal_state),
        "exit_clarity": score_exit_clarity(ideal_state),
        "intent_alignment": score_intent_alignment(ideal_state),
    }

    # Calculate weighted overall score
    overall_score = sum(
        dimension_scores[dim] * weight for dim, weight in COMPLETENESS_WEIGHTS.items()
    )

    # Identify missing elements
    missing_elements = []
    recommendations = []

    if dimension_scores["criteria_clarity"] < 0.8:
        missing_elements.append("Clear success criteria")
        recommendations.append(
            "Define at least 2 success criteria with verification methods"
        )

    if dimension_scores["metric_precision"] < 0.7:
        missing_elements.append("Precise metrics")
        recommendations.append("Add quantifiable metrics with target values")

    if dimension_scores["verification_feasibility"] < 0.7:
        missing_elements.append("Feasible verification")
        recommendations.append("Ensure criteria can be objectively verified")

    if dimension_scores["anti_criteria_coverage"] < 0.5:
        missing_elements.append("Anti-criteria")
        recommendations.append("Identify what should NOT happen")

    if dimension_scores["exit_clarity"] < 0.5:
        missing_elements.append("Exit conditions")
        recommendations.append("Define clear exit conditions")

    if dimension_scores["intent_alignment"] < 0.8:
        missing_elements.append("Intent clarity")
        recommendations.append("Clarify objective and desired outcome")

    return CompletenessResult(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        missing_elements=missing_elements,
        ready_to_proceed=overall_score >= COMPLETENESS_THRESHOLD,
        recommendations=recommendations,
    )
