"""
perform-tdd Session Complete Script

Completes or loops back a TDD session.
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
from orchestration.utils import load_content, substitute_placeholders


def main() -> None:
    """Main entry point for session completion."""
    parser = argparse.ArgumentParser(description="Complete perform-tdd Session")
    parser.add_argument(
        "--perform-tdd-state",
        required=True,
        help="TDD session ID",
    )
    parser.add_argument(
        "--loop-back",
        action="store_true",
        help="Loop back to RED for next feature instead of completing",
    )
    args = parser.parse_args()

    # Load state
    state = TDDState.load(args.perform_tdd_state)
    if not state:
        print(f"ERROR: TDD session {args.perform_tdd_state} not found", file=sys.stderr)
        sys.exit(1)

    current_phase = state.current_phase

    if args.loop_back:
        # Loop back to RED
        if current_phase != TDDPhase.DOC:
            print(
                f"ERROR: Can only loop back from DOC phase, current: {current_phase.name}",
                file=sys.stderr,
            )
            sys.exit(1)

        if not state.loop_back_to_red():
            print("ERROR: Loop-back failed", file=sys.stderr)
            sys.exit(1)

        # CRITICAL: Save state BEFORE printing directive
        state.save()

        # Print RED phase content for new cycle
        content = load_content(__file__, "phase_red.md")
        prompt = substitute_placeholders(
            content,
            session_id=state.session_id,
            target_file=state.target_file or "(not specified)",
            test_file=state.test_file or "(not specified)",
            cycle_count=str(state.cycle_count),
            parent_algorithm_id=state.parent_algorithm_id or "(none)",
        )
        print(prompt)
    else:
        # Complete the session
        if current_phase != TDDPhase.DOC:
            print(
                f"ERROR: Can only complete from DOC phase, current: {current_phase.name}",
                file=sys.stderr,
            )
            sys.exit(1)

        if not state.advance_to_phase(TDDPhase.COMPLETED):
            print("ERROR: Transition to COMPLETED failed", file=sys.stderr)
            sys.exit(1)

        # CRITICAL: Save state BEFORE printing directive
        state.save()

        print(f"""
TDD Session Completed
=====================

- Session ID: {state.session_id}
- Cycles completed: {state.cycle_count + 1}
- Target file: {state.target_file or "(not specified)"}
- Test file: {state.test_file or "(not specified)"}

Phase outputs recorded:
{list(state.phase_outputs.keys())}
""")


if __name__ == "__main__":
    main()
