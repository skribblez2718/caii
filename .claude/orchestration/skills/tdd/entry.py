"""
TDD Skill Entry Point

Main entry point for TDD skill. Creates or loads TDD state
and routes to appropriate phase content.
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

from orchestration.skills.tdd.tdd_state import TDDPhase, TDDState
from orchestration.utils import load_content, substitute_placeholders

# Phase to content file mapping
PHASE_CONTENT_MAP = {
    TDDPhase.INITIALIZED: "phase_red.md",  # Start with RED
    TDDPhase.RED: "phase_red.md",
    TDDPhase.GREEN: "phase_green.md",
    TDDPhase.REFACTOR: "phase_refactor.md",
    TDDPhase.DOC: "phase_doc.md",
    TDDPhase.COMPLETED: None,  # No content for completed
}


def main() -> None:
    """Main entry point for TDD skill."""
    parser = argparse.ArgumentParser(description="TDD Skill Entry Point")
    parser.add_argument(
        "--algorithm-state",
        required=True,
        help="Parent algorithm session ID",
    )
    parser.add_argument(
        "--tdd-state",
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
    args = parser.parse_args()

    # Load or create TDD state
    if args.tdd_state:
        state = TDDState.load(args.tdd_state)
        if not state:
            print(f"ERROR: TDD session {args.tdd_state} not found", file=sys.stderr)
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

    # Get content file for current phase
    content_file = PHASE_CONTENT_MAP.get(state.current_phase)
    if not content_file:
        print("TDD cycle completed.")
        return

    # Load and print phase content
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
