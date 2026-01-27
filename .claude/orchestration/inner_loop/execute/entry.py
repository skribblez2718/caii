"""
EXECUTE Phase Entry Point (Step 5)

Task execution.
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

from orchestration.state import AlgorithmState
from orchestration.utils import load_content, substitute_placeholders

# Step number for this phase
STEP_NUM = 5


def main() -> None:
    parser = argparse.ArgumentParser(description="EXECUTE Phase (Step 5)")
    parser.add_argument("--state", required=True, help="Session ID for state tracking")
    parser.add_argument("user_query", nargs="?", default="", help="User query (legacy)")
    args = parser.parse_args()

    # Load state
    state = AlgorithmState.load(args.state)
    if not state:
        print(f"ERROR: Session {args.state} not found", file=sys.stderr)
        sys.exit(1)

    # Start this phase
    if not state.start_phase(STEP_NUM):
        print("ERROR: Cannot transition to EXECUTE phase", file=sys.stderr)
        print(f"Current phase: {state.current_phase.name}", file=sys.stderr)
        sys.exit(1)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Load and print phase content
    content = load_content(__file__, "execute_phase.md")
    prompt = substitute_placeholders(
        content,
        user_query=state.user_query,
        session_id=state.session_id,
    )
    print(prompt)


if __name__ == "__main__":
    main()
