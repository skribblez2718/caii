"""
perform-tdd Skill Entry Point

Main entry point for perform-tdd skill. Creates or loads TDD state
and routes to appropriate phase content, triggering agent flows.
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

from orchestration.skills.perform_tdd.tdd_state import TDDPhase, TDDState
from orchestration.skills.perform_tdd.flows import get_flow_for_phase
from orchestration.agent_chain.orchestrator import ChainOrchestrator
from orchestration.utils import load_content, substitute_placeholders

# Phase to content file mapping (for legacy phase content display)
PHASE_CONTENT_MAP = {
    TDDPhase.INITIALIZED: "phase_red.md",  # Start with RED
    TDDPhase.RED: "phase_red.md",
    TDDPhase.GREEN: "phase_green.md",
    TDDPhase.REFACTOR: "phase_refactor.md",
    TDDPhase.DOC: "phase_doc.md",
    TDDPhase.COMPLETED: None,  # No content for completed
}

# Phase to flow mapping
PHASE_FLOW_MAP = {
    TDDPhase.RED: "RED",
    TDDPhase.GREEN: "GREEN",
    TDDPhase.REFACTOR: "REFACTOR",
    TDDPhase.DOC: "DOC",
}

# Content directory for agent-specific content
CONTENT_DIR = Path(__file__).parent / "content"


def main() -> None:
    """Main entry point for perform-tdd skill."""
    parser = argparse.ArgumentParser(description="perform-tdd Skill Entry Point")
    parser.add_argument(
        "--algorithm-state",
        required=True,
        help="Parent algorithm session ID",
    )
    parser.add_argument(
        "--perform-tdd-state",
        help="Existing TDD session ID to resume",
    )
    parser.add_argument(
        "--target",
        help="Target implementation file path",
    )
    parser.add_argument(
        "--test",
        help="Test file path",
    )
    parser.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip agent flow (legacy mode - just print phase content)",
    )
    args = parser.parse_args()

    # Load or create TDD state
    if args.perform_tdd_state:
        state = TDDState.load(args.perform_tdd_state)
        if not state:
            print(
                f"ERROR: TDD session {args.perform_tdd_state} not found",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        state = TDDState(
            parent_algorithm_id=args.algorithm_state,
            target_file=args.target,
            test_file=args.test,
        )

    # If in INITIALIZED, advance to RED
    if state.current_phase == TDDPhase.INITIALIZED:
        state.advance_to_phase(TDDPhase.RED)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Get current phase
    current_phase = state.current_phase

    # Check if completed
    if current_phase == TDDPhase.COMPLETED:
        print("TDD cycle completed.")
        return

    # Print phase header
    print(f"## TDD {current_phase.name} Phase")
    print()
    print(f"**Session:** {state.session_id}")
    print(f"**Cycle:** {state.cycle_count}")
    if state.target_file:
        print(f"**Target:** {state.target_file}")
    if state.test_file:
        print(f"**Test:** {state.test_file}")
    print()

    # Legacy mode: just print phase content
    if args.no_flow:
        content_file = PHASE_CONTENT_MAP.get(current_phase)
        if content_file:
            content = load_content(__file__, content_file)
            prompt = substitute_placeholders(
                content,
                session_id=state.session_id,
                target_file=state.target_file or "(not specified)",
                test_file=state.test_file or "(not specified)",
                cycle_count=str(state.cycle_count),
                parent_algorithm_id=state.parent_algorithm_id or "(none)",
            )
            print(prompt)
        return

    # Agent flow mode: trigger the agent chain for this phase
    phase_name = PHASE_FLOW_MAP.get(current_phase)
    if not phase_name:
        print(f"ERROR: No flow defined for phase {current_phase.name}", file=sys.stderr)
        sys.exit(1)

    try:
        flow = get_flow_for_phase(phase_name)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Build task description
    task_description = f"TDD {phase_name} phase"
    if state.target_file:
        task_description += f" for {state.target_file}"

    # Create orchestrator and start flow
    orchestrator = ChainOrchestrator(
        flow=flow,
        task_id=state.session_id,
        skill_content_dir=CONTENT_DIR,
        skill_name="perform-tdd",
        phase_id=phase_name.lower(),
        domain="technical",
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
