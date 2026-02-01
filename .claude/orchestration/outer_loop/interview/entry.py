"""
INTERVIEW Phase Entry Point (Step 0.5)

Unified requirements gathering and IDEAL STATE capture.
Iterates until 95% completeness or max 5 iterations.

Flow:
1. Load algorithm state (must have GATHER completed)
2. Run clarification -> validation flow
3. Check completeness score
4. If < 95% and iterations < 5, loop with refinement flow
5. When complete, proceed to INNER_LOOP
"""

import argparse
import sys
from pathlib import Path

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

# pylint: disable=wrong-import-position
from orchestration.state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.agent_chain.orchestrator import ChainOrchestrator
from orchestration.outer_loop.interview.flows import get_interview_flow
from orchestration.outer_loop.interview.completeness_scorer import (
    COMPLETENESS_THRESHOLD,
    MAX_INTERVIEW_ITERATIONS,
)

# Step number for this phase
STEP_NUM = 0.5

# Content directory for agent-specific content
CONTENT_DIR = Path(__file__).parent / "content"


def main() -> None:  # pylint: disable=too-many-statements
    """INTERVIEW phase entry point."""
    parser = argparse.ArgumentParser(description="INTERVIEW Phase (Step 0.5)")
    parser.add_argument(
        "--state",
        required=True,
        help="Algorithm session ID",
    )
    parser.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip agent flow (legacy mode - just print info)",
    )
    args = parser.parse_args()

    # Load algorithm state
    state = AlgorithmState.load(args.state)
    if not state:
        print(f"ERROR: Session {args.state} not found", file=sys.stderr)
        sys.exit(1)

    # Verify we're in correct phase
    valid_phases = [
        AlgorithmPhase.GATHER,
        AlgorithmPhase.INTERVIEW,
        AlgorithmPhase.GET_STATE,  # Legacy
        AlgorithmPhase.IDEAL_STATE,  # Legacy
    ]
    if state.current_phase not in valid_phases:
        print(
            f"ERROR: Cannot start INTERVIEW from {state.current_phase.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Transition to INTERVIEW phase if needed
    if state.current_phase in [
        AlgorithmPhase.GATHER,
        AlgorithmPhase.GET_STATE,  # Legacy
    ]:
        if not state.start_phase(AlgorithmPhase.INTERVIEW):
            print("ERROR: Cannot transition to INTERVIEW phase", file=sys.stderr)
            sys.exit(1)

    # Get current iteration
    iteration = state.interview_iteration

    # Check iteration limit
    if iteration >= MAX_INTERVIEW_ITERATIONS:
        print(
            f"WARNING: Max iterations ({MAX_INTERVIEW_ITERATIONS}) reached",
            file=sys.stderr,
        )
        # Force proceed with current state
        iteration = MAX_INTERVIEW_ITERATIONS - 1

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Print phase header
    print("## INTERVIEW Phase (Step 0.5)")
    print()
    print(f"**Session:** {state.session_id}")
    print(f"**Iteration:** {iteration + 1} of {MAX_INTERVIEW_ITERATIONS}")
    print(f"**Completeness Target:** {COMPLETENESS_THRESHOLD * 100:.0f}%")
    print()

    if state.ideal_state:
        print(f"**Current Objective:** {state.ideal_state.objective[:80]}...")
        print(f"**Completeness:** {state.ideal_state.completeness_score * 100:.0f}%")
        print()

    # Legacy mode: just print info
    if args.no_flow:
        print("### INTERVIEW Requirements")
        print()
        print("**Goal:** Capture IDEAL STATE with 95% completeness")
        print()
        print("**Dimensions Evaluated:**")
        print("- Criteria Clarity (25%)")
        print("- Metric Precision (20%)")
        print("- Verification Feasibility (20%)")
        print("- Anti-Criteria Coverage (15%)")
        print("- Exit Clarity (10%)")
        print("- Intent Alignment (10%)")
        print()
        print("In legacy mode - agent flow not triggered.")
        return

    # Get appropriate flow for this iteration
    flow = get_interview_flow(iteration)

    # Build task description
    if iteration == 0:
        task_description = "Capture IDEAL STATE requirements"
    else:
        task_description = f"Refine IDEAL STATE (iteration {iteration + 1})"

    # Create orchestrator
    orchestrator = ChainOrchestrator(
        flow=flow,
        task_id=state.session_id,
        skill_content_dir=CONTENT_DIR,
        skill_name="outer-loop",
        phase_id="interview",
        domain=state.task_domain or "general",
        task_description=task_description,
    )

    # Print flow info
    print("---")
    print()
    print(f"**Flow:** {flow.name} (`{flow.flow_id}`)")
    print(f"**Agents:** {' → '.join(s.agent_name for s in flow.steps)}")
    print()

    # Start the flow
    directive = orchestrator.start_flow()
    print(directive)


if __name__ == "__main__":
    main()
