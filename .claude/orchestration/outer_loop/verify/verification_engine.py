"""
4-Layer Verification Engine

Implements the 4-layer verification system:
- Layer 1 (Objective): 50% weight - Automatable checks (syntax, tests, format)
- Layer 2 (Heuristic): 30% weight - Pattern-based rules (complexity, style)
- Layer 3 (Semantic): 20% weight - LLM-judged (intent match, reasoning clarity)
- Layer 4 (User): Final confirmation (not in scoring - handled separately)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from orchestration.state.algorithm_state import (
    IdealState,
    VerificationResult,
)


class VerificationEngine:
    """
    4-layer verification engine for comparing output against IDEAL STATE.

    Weights:
        - Objective: 50%
        - Heuristic: 30%
        - Semantic: 20%
    """

    OBJECTIVE_WEIGHT = 0.5
    HEURISTIC_WEIGHT = 0.3
    SEMANTIC_WEIGHT = 0.2

    # Thresholds for status determination
    VERIFIED_THRESHOLD = 0.9
    GAPS_THRESHOLD = 0.6

    def verify(
        self,
        ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
        iteration: int,
    ) -> VerificationResult:
        """
        Verify phase outputs against IDEAL STATE.

        Args:
            ideal_state: The IDEAL STATE specification
            phase_outputs: Outputs from execution phases (BUILD, EXECUTE, etc.)
            iteration: Current verification iteration

        Returns:
            VerificationResult with status, scores, gaps, and recommendations

        Raises:
            ValueError: If ideal_state is None
        """
        if ideal_state is None:
            raise ValueError("ideal_state cannot be None")

        # Check for anti-criteria violations first
        anti_criteria_violated = self._check_anti_criteria(ideal_state, phase_outputs)

        # Evaluate each layer
        objective_score = self._evaluate_objective_layer(ideal_state, phase_outputs)
        heuristic_score = self._evaluate_heuristic_layer(ideal_state, phase_outputs)
        semantic_score = self._evaluate_semantic_layer(ideal_state, phase_outputs)

        # Calculate weighted overall score
        overall_score = (
            objective_score * self.OBJECTIVE_WEIGHT
            + heuristic_score * self.HEURISTIC_WEIGHT
            + semantic_score * self.SEMANTIC_WEIGHT
        )

        # Determine status
        if anti_criteria_violated:
            status = "CRITICAL_FAILURE"
        elif overall_score >= self.VERIFIED_THRESHOLD:
            status = "VERIFIED"
        elif overall_score >= self.GAPS_THRESHOLD:
            status = "GAPS_IDENTIFIED"
        else:
            status = "CRITICAL_FAILURE"

        # Generate gaps and recommendations
        gaps = self._identify_gaps(ideal_state, phase_outputs, overall_score)
        recommendations = self._generate_recommendations(gaps, status)

        return VerificationResult(
            iteration=iteration,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            objective_score=objective_score,
            heuristic_score=heuristic_score,
            semantic_score=semantic_score,
            overall_score=overall_score,
            gaps=gaps,
            recommendations=recommendations,
        )

    def _check_anti_criteria(
        self,
        _ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
    ) -> bool:
        """
        Check if any anti-criteria have been violated.

        Args:
            ideal_state: IDEAL STATE with anti-criteria
            phase_outputs: Phase outputs to check

        Returns:
            True if any anti-criteria violated
        """
        # Check for explicit anti-criteria violations in outputs
        for _phase_name, outputs in phase_outputs.items():
            if isinstance(outputs, dict):
                violations = outputs.get("anti_criteria_violations", [])
                if violations:
                    return True

        return False

    def _evaluate_objective_layer(
        self,
        _ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
    ) -> float:
        """
        Evaluate Layer 1: Objective (automatable checks).

        Checks:
        - Syntax validation
        - Test execution results
        - Format compliance

        Args:
            ideal_state: IDEAL STATE specification
            phase_outputs: Phase outputs to check

        Returns:
            Score from 0.0 to 1.0
        """
        if not phase_outputs:
            return 0.0

        scores: List[float] = []

        # Check test results
        for _phase_name, outputs in phase_outputs.items():
            if isinstance(outputs, dict):
                test_results = outputs.get("test_results", {})
                if test_results:
                    passed = test_results.get("passed", 0)
                    failed = test_results.get("failed", 0)
                    total = passed + failed
                    if total > 0:
                        scores.append(passed / total)

                # Check execution status
                status = outputs.get("status", "")
                if status == "completed":
                    scores.append(1.0)
                elif status == "failed":
                    scores.append(0.0)

                # Check if all criteria met flag
                if outputs.get("all_criteria_met"):
                    scores.append(1.0)

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def _evaluate_heuristic_layer(
        self,
        _ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
    ) -> float:
        """
        Evaluate Layer 2: Heuristic (pattern-based rules).

        Checks:
        - Code complexity
        - Style guide compliance
        - Pattern matching

        Args:
            ideal_state: IDEAL STATE specification
            phase_outputs: Phase outputs to check

        Returns:
            Score from 0.0 to 1.0
        """
        if not phase_outputs:
            return 0.5  # Neutral score when no outputs

        scores: List[float] = []

        # Check for heuristic indicators in outputs
        for _phase_name, outputs in phase_outputs.items():
            if isinstance(outputs, dict):
                # Check lint results if present
                lint_score = outputs.get("lint_score")
                if lint_score is not None:
                    scores.append(float(lint_score) / 10.0)

                # Check complexity metrics
                complexity = outputs.get("complexity_score")
                if complexity is not None:
                    # Lower complexity is better (invert)
                    scores.append(max(0.0, 1.0 - (float(complexity) / 100.0)))

                # Check files created (presence is a positive indicator)
                files_created = outputs.get("files_created", [])
                if files_created:
                    scores.append(0.8)

        if not scores:
            return 0.7  # Default reasonable score

        return sum(scores) / len(scores)

    def _evaluate_semantic_layer(
        self,
        _ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
    ) -> float:
        """
        Evaluate Layer 3: Semantic (LLM-judged).

        Checks:
        - Intent alignment
        - Reasoning clarity

        Note: In production, this would call an LLM for evaluation.
        For now, returns a reasonable default based on available data.

        Args:
            ideal_state: IDEAL STATE specification
            phase_outputs: Phase outputs to check

        Returns:
            Score from 0.0 to 1.0
        """
        if not phase_outputs:
            return 0.5  # Neutral when no data

        # Check for explicit semantic evaluations in outputs
        for _phase_name, outputs in phase_outputs.items():
            if isinstance(outputs, dict):
                semantic_score = outputs.get("semantic_score")
                if semantic_score is not None:
                    return float(semantic_score)

                # Check for intent match flag
                if outputs.get("intent_matched"):
                    return 0.9

        # Default semantic score based on other indicators
        # In production, this would involve LLM evaluation
        return 0.7

    def _identify_gaps(
        self,
        ideal_state: IdealState,
        phase_outputs: Dict[str, Any],
        overall_score: float,
    ) -> List[str]:
        """
        Identify specific gaps between output and IDEAL STATE.

        Args:
            ideal_state: IDEAL STATE specification
            phase_outputs: Phase outputs
            overall_score: Overall verification score

        Returns:
            List of identified gaps
        """
        gaps: List[str] = []

        # Check success criteria
        for criterion in ideal_state.success_criteria:
            if not criterion.verified:
                gaps.append(f"Unverified: {criterion.description}")

        # Check test results
        for phase_name, outputs in phase_outputs.items():
            if isinstance(outputs, dict):
                test_results = outputs.get("test_results", {})
                failed = test_results.get("failed", 0)
                if failed > 0:
                    gaps.append(f"{failed} tests failing in {phase_name}")

                # Check for explicit gaps
                explicit_gaps = outputs.get("gaps", [])
                gaps.extend(explicit_gaps)

        # Add gap if overall score is low
        if overall_score < self.GAPS_THRESHOLD:
            gaps.append(f"Overall score ({overall_score:.2f}) below threshold")

        return gaps

    def _generate_recommendations(
        self,
        gaps: List[str],
        status: str,
    ) -> List[str]:
        """
        Generate recommendations based on identified gaps.

        Args:
            gaps: List of identified gaps
            status: Verification status

        Returns:
            List of recommendations
        """
        recommendations: List[str] = []

        if status == "CRITICAL_FAILURE":
            recommendations.append("Review anti-criteria violations immediately")
            recommendations.append("Consider major refactoring or redesign")

        for gap in gaps:
            if "test" in gap.lower():
                recommendations.append("Fix failing tests before proceeding")
            elif "unverified" in gap.lower():
                recommendations.append(f"Address: {gap}")

        if not recommendations and status == "GAPS_IDENTIFIED":
            recommendations.append("Review and address identified gaps")

        return recommendations
