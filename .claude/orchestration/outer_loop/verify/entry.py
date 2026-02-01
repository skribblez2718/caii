"""
Verification Entry Point (Step 8)

Verifies output against IDEAL STATE criteria.
Includes loop-back logic and question bubble-up.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

from orchestration.entry_base import PhaseConfig, run_phase_entry
from orchestration.outer_loop.verify.flows import VERIFY_FLOW
from orchestration.outer_loop.verify.feedback_generator import FeedbackGenerator
from orchestration.outer_loop.verify.question_aggregator import QuestionAggregator
from orchestration.state.algorithm_state import (
    AlgorithmState,
    PendingQuestion,
    VerificationResult,
)
from orchestration.state.algorithm_fsm import AlgorithmPhase

# Step number for this phase (preserved for backward compatibility)
STEP_NUM = 8

# Maximum iterations for loop-back
MAX_VERIFY_ITERATIONS = 3


def _verify_extra_placeholders(state: Any) -> Dict[str, Any]:
    """Extra placeholders for VERIFY phase (backward compatibility)."""
    return {"task_id": state.session_id}


# Phase configuration with agent flow
VERIFY_FLOW_CONFIG = PhaseConfig(
    phase=AlgorithmPhase.VERIFY,
    phase_name="VERIFY",
    content_file="verification.md",
    description="VERIFY Phase (Step 8)",
    extra_placeholders=_verify_extra_placeholders,
    agent_flow=VERIFY_FLOW,
    skill_name="outer-loop",
    skill_content_dir=Path(__file__).parent.parent / "content",
)


def validate_verification_preconditions(
    state: AlgorithmState,
) -> Tuple[bool, str]:
    """
    Validate that preconditions for verification are met.

    Args:
        state: Current algorithm state

    Returns:
        Tuple of (is_valid, error_message)
    """
    if state.ideal_state is None:
        return False, "Cannot verify: ideal_state not defined"

    return True, ""


def handle_verification_result(
    state: AlgorithmState,
    result: VerificationResult,
) -> str:
    """
    Handle verification result and determine next action.

    Args:
        state: Current algorithm state
        result: Verification result

    Returns:
        Action string: "PROCEED", "LOOP_BACK", or "ESCALATE"
    """
    generator = FeedbackGenerator()
    decision = generator.generate(
        result,
        iteration=state.verify_iteration,
        max_iterations=MAX_VERIFY_ITERATIONS,
    )

    return decision.action


def execute_loop_back(
    state: AlgorithmState,
    result: Optional[VerificationResult] = None,
) -> None:
    """
    Execute loop-back from VERIFY to INNER_LOOP.

    Args:
        state: Algorithm state to update
        result: Optional verification result to add to history
    """
    if result:
        state.add_verification_result(result)

    state.loop_back_to_inner_loop()
    state.save()


def aggregate_inner_loop_questions(
    state: AlgorithmState,
    memory_files: List[Path],
) -> List[PendingQuestion]:
    """
    Aggregate questions from inner loop memory files.

    Args:
        state: Current algorithm state
        memory_files: List of memory file paths

    Returns:
        List of PendingQuestion objects
    """
    aggregator = QuestionAggregator()
    bubble_up = aggregator.aggregate(memory_files, state.session_id)

    pending: List[PendingQuestion] = []
    for q in bubble_up.questions:
        pending.append(
            PendingQuestion(
                id=q.id,
                priority=q.priority,
                question=q.question,
                context=q.context,
                options=q.options,
                discovered_by=q.discovered_by,
                discovery_phase=q.discovery_phase,
            )
        )

    return pending


def add_questions_to_state(
    state: AlgorithmState,
    questions: List[PendingQuestion],
) -> None:
    """
    Add questions to state's pending_questions.

    Args:
        state: Algorithm state to update
        questions: Questions to add
    """
    for question in questions:
        state.add_pending_question(question)


if __name__ == "__main__":
    run_phase_entry(
        __file__,
        VERIFY_FLOW_CONFIG,
    )
