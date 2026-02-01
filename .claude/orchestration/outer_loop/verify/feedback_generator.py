"""
Feedback Generator

Converts VerificationResult to actionable next steps:
- PROCEED: Continue to LEARN phase
- LOOP_BACK: Return to INNER_LOOP for refinement
- ESCALATE: Require user intervention
"""

from dataclasses import dataclass, field
from typing import List

from orchestration.state.algorithm_state import VerificationResult


@dataclass
class FeedbackDecision:
    """Decision from feedback generator."""

    action: str  # PROCEED, LOOP_BACK, ESCALATE
    message: str  # Human-readable explanation
    next_phase: str  # LEARN, INNER_LOOP, USER_REVIEW
    gaps: List[str] = field(default_factory=list)


class FeedbackGenerator:
    """
    Generates feedback decisions based on verification results.

    Decision logic:
    - VERIFIED -> PROCEED to LEARN
    - GAPS_IDENTIFIED + iteration < max -> LOOP_BACK to INNER_LOOP
    - GAPS_IDENTIFIED + iteration >= max -> ESCALATE to USER_REVIEW
    - CRITICAL_FAILURE -> ESCALATE immediately
    """

    DEFAULT_MAX_ITERATIONS = 3

    def generate(
        self,
        verification_result: VerificationResult,
        iteration: int,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ) -> FeedbackDecision:
        """
        Generate feedback decision based on verification result.

        Args:
            verification_result: Result from verification engine
            iteration: Current iteration number
            max_iterations: Maximum allowed iterations (default 3)

        Returns:
            FeedbackDecision with action, message, next_phase, and gaps
        """
        status = verification_result.status
        gaps = list(verification_result.gaps)

        if status == "VERIFIED":
            return FeedbackDecision(
                action="PROCEED",
                message="All verification criteria met. Proceeding to LEARN phase.",
                next_phase="LEARN",
                gaps=[],
            )

        if status == "CRITICAL_FAILURE":
            return FeedbackDecision(
                action="ESCALATE",
                message=(
                    "Critical failure detected. "
                    "User intervention required to resolve anti-criteria violations."
                ),
                next_phase="USER_REVIEW",
                gaps=gaps,
            )

        # GAPS_IDENTIFIED
        if iteration >= max_iterations:
            return FeedbackDecision(
                action="ESCALATE",
                message=(
                    f"Maximum iterations ({max_iterations}) reached. "
                    "Gaps remain unresolved. User review required."
                ),
                next_phase="USER_REVIEW",
                gaps=gaps,
            )

        # Can still loop back
        gap_summary = "; ".join(gaps[:3]) if gaps else "Gaps identified in verification"
        return FeedbackDecision(
            action="LOOP_BACK",
            message=(
                f"Gaps identified (iteration {iteration}/{max_iterations}): "
                f"{gap_summary}. Returning to INNER_LOOP for refinement."
            ),
            next_phase="INNER_LOOP",
            gaps=gaps,
        )
