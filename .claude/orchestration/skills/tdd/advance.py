"""
TDD Phase Advance Script

Advances TDD state to the next phase in the cycle.
Called after phase completion to transition FSM.
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

from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState
from orchestration.utils import load_content, substitute_placeholders

# Next phase mapping
NEXT_PHASE = {
    TDDPhase.RED: TDDPhase.GREEN,
    TDDPhase.GREEN: TDDPhase.REFACTOR,
    TDDPhase.REFACTOR: TDDPhase.DOC,
    TDDPhase.DOC: TDDPhase.COMPLETED,
}

# Phase to content file mapping
PHASE_CONTENT_MAP = {
    TDDPhase.RED: "phase_red.md",
    TDDPhase.GREEN: "phase_green.md",
    TDDPhase.REFACTOR: "phase_refactor.md",
    TDDPhase.DOC: "phase_doc.md",
    TDDPhase.COMPLETED: None,
}


def main() -> None:
    """Main entry point for phase advancement."""
    parser = argparse.ArgumentParser(description="Advance TDD Phase")
    parser.add_argument(
        "--tdd-state",
        required=True,
        help="TDD session ID",
    )
    parser.add_argument(
        "--output",
        help="JSON string of phase output to record",
    )
    args = parser.parse_args()

    # Load state
    state = TDDState.load(args.tdd_state)
    if not state:
        print(f"ERROR: TDD session {args.tdd_state} not found", file=sys.stderr)
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

    # Print next phase content
    content_file = PHASE_CONTENT_MAP.get(next_phase)
    if not content_file:
        print(f"TDD cycle completed. Session: {state.session_id}")
        return

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


if __name__ == "__main__":
    main()
