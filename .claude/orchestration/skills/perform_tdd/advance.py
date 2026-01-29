"""
perform-tdd Phase Advance Script

Advances TDD state to the next phase in the cycle.
Called after phase completion to transition FSM.

Uses invoke_agent_flow to trigger agent chains for each phase.
"""

import argparse
import json
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
from orchestration.flow_invoker import invoke_agent_flow, get_flow_directive_info

# Next phase mapping
NEXT_PHASE = {
    TDDPhase.RED: TDDPhase.GREEN,
    TDDPhase.GREEN: TDDPhase.REFACTOR,
    TDDPhase.REFACTOR: TDDPhase.DOC,
    TDDPhase.DOC: TDDPhase.COMPLETED,
}

# Phase to flow name mapping
PHASE_FLOW_MAP = {
    TDDPhase.RED: "RED",
    TDDPhase.GREEN: "GREEN",
    TDDPhase.REFACTOR: "REFACTOR",
    TDDPhase.DOC: "DOC",
}

# Content directory for agent-specific content
CONTENT_DIR = Path(__file__).parent / "content"


def main() -> None:
    """Main entry point for phase advancement."""
    parser = argparse.ArgumentParser(description="Advance perform-tdd Phase")
    parser.add_argument(
        "--perform-tdd-state",
        required=True,
        help="TDD session ID",
    )
    parser.add_argument(
        "--output",
        help="JSON string of phase output to record",
    )
    parser.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip agent flow (legacy mode)",
    )
    args = parser.parse_args()

    # Load state
    state = TDDState.load(args.perform_tdd_state)
    if not state:
        print(f"ERROR: TDD session {args.perform_tdd_state} not found", file=sys.stderr)
        sys.exit(1)

    # Record output if provided
    if args.output:
        try:
            output_data = json.loads(args.output)
            state.record_phase_output(state.current_phase, output_data)
        except json.JSONDecodeError:
            print(f"WARNING: Invalid JSON output: {args.output}", file=sys.stderr)

    current_phase = state.current_phase

    # Get next phase
    next_phase = NEXT_PHASE.get(current_phase)
    if not next_phase:
        print(f"ERROR: No next phase from {current_phase.name}", file=sys.stderr)
        sys.exit(1)

    # Advance to next phase
    if not state.advance_to_phase(next_phase):
        print(
            f"ERROR: Cannot transition from {current_phase.name} to {next_phase.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Check if completed
    if next_phase == TDDPhase.COMPLETED:
        print(f"TDD cycle completed. Session: {state.session_id}")
        return

    # Print phase header
    print(f"## TDD {next_phase.name} Phase")
    print()
    print(f"**Session:** {state.session_id}")
    print(f"**Cycle:** {state.cycle_count}")
    if state.target_file:
        print(f"**Target:** {state.target_file}")
    if state.test_file:
        print(f"**Test:** {state.test_file}")
    print()

    # Legacy mode: skip agent flow (for backwards compatibility)
    if args.no_flow:
        from orchestration.utils import load_content, substitute_placeholders

        # Legacy content file mapping
        PHASE_CONTENT_MAP = {
            TDDPhase.RED: "phase_red.md",
            TDDPhase.GREEN: "phase_green.md",
            TDDPhase.REFACTOR: "phase_refactor.md",
            TDDPhase.DOC: "phase_doc.md",
        }

        content_file = PHASE_CONTENT_MAP.get(next_phase)
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
    phase_name = PHASE_FLOW_MAP.get(next_phase)
    if not phase_name:
        print(f"ERROR: No flow defined for phase {next_phase.name}", file=sys.stderr)
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

    # Print flow info
    print("---")
    print()
    print(get_flow_directive_info(flow))
    print()

    # Invoke the agent flow
    directive = invoke_agent_flow(
        flow=flow,
        task_id=state.session_id,
        skill_name="perform-tdd",
        phase_id=phase_name.lower(),
        skill_content_dir=CONTENT_DIR,
        task_description=task_description,
    )
    print(directive)


if __name__ == "__main__":
    main()
