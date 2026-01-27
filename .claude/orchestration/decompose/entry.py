"""
Decompose Protocol Entry Point (STUB)

Breaks complex/very_complex tasks into 2+ simpler subtasks.
Each subtask is re-analyzed for complexity.

TODO: Implement in future session
"""

import argparse
import sys

from orchestration.state import AlgorithmState


def main() -> None:
    """Entry point for DECOMPOSE protocol."""
    parser = argparse.ArgumentParser(description="DECOMPOSE Protocol Entry Point")
    parser.add_argument("--state", required=True, help="Session ID to load")
    args = parser.parse_args()

    state = AlgorithmState.load(args.state)
    if not state:
        print(f"ERROR: Session {args.state} not found", file=sys.stderr)
        sys.exit(1)

    # STUB: Print placeholder message
    complexity_display = (
        state.complexity.replace("_", " ") if state.complexity else "unknown"
    )

    print("\n## DECOMPOSE Protocol (STUB)")
    print(f"\n**Task Complexity:** {complexity_display}")
    print(f"**User Query:** {state.user_query}")
    print(f"**Session:** {state.session_id}")

    print("\n### Status: Not Yet Implemented")
    print("\n**TODO:** Implement decomposition logic in future session.")

    print("\n### Expected Behavior When Implemented")
    print("1. Analyze task to identify natural decomposition points")
    print("2. Output 2+ subtasks, each targeting complexity <= moderate")
    print("3. Each subtask re-enters complexity analysis")
    print("4. Only subtasks <= moderate proceed to GATHER")

    if state.decomposition_required:
        print(
            "\n**Note:** This task is marked as `very_complex` - decomposition is REQUIRED."
        )
    else:
        print(
            "\n**Note:** This task is marked as `complex` - decomposition is RECOMMENDED."
        )


if __name__ == "__main__":
    main()
