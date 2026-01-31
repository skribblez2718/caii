"""
DECOMPOSE Protocol Entry Point

Breaks complex/very_complex tasks into SIMPLE subtasks using agent flows.
Each subtask is then routed through GATHER for full algorithm treatment.
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

from orchestration.decompose.flows import DECOMPOSE_FLOW
from orchestration.flow_invoker import invoke_agent_flow
from orchestration.state import AlgorithmState

# Content directory for decompose protocol content
CONTENT_DIR = Path(__file__).parent / "content"


def main() -> None:
    """Entry point for DECOMPOSE protocol."""
    parser = argparse.ArgumentParser(description="DECOMPOSE Protocol Entry Point")
    parser.add_argument("--state", required=True, help="Session ID to load")
    parser.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip agent flow (legacy mode - just print status)",
    )
    args = parser.parse_args()

    state = AlgorithmState.load(args.state)
    if not state:
        print(f"ERROR: Session {args.state} not found", file=sys.stderr)
        sys.exit(1)

    # Display protocol header
    complexity_display = (
        state.complexity.replace("_", " ") if state.complexity else "unknown"
    )

    print("## DECOMPOSE Protocol")
    print()
    print(f"**Task Complexity:** {complexity_display}")
    print(f"**Session:** {state.session_id}")
    print(f"**User Query:** {state.user_query}")
    print()

    # Legacy mode: just print status
    if args.no_flow:
        _print_legacy_status(state)
        return

    # Agent flow mode: trigger DECOMPOSE_FLOW
    print("---")
    print()
    print(f"**Flow:** {DECOMPOSE_FLOW.name} (`{DECOMPOSE_FLOW.flow_id}`)")
    print(f"**Agents:** {' → '.join(s.agent_name for s in DECOMPOSE_FLOW.steps)}")
    print()

    # Build task description
    task_description = f"Decompose {complexity_display} task into SIMPLE subtasks"

    # Invoke agent flow
    directive = invoke_agent_flow(
        flow=DECOMPOSE_FLOW,
        task_id=state.session_id,
        skill_name="decompose",
        phase_id="decompose",
        domain="technical",
        task_description=task_description,
        skill_content_dir=CONTENT_DIR,
    )

    print(directive)


def _print_legacy_status(state: AlgorithmState) -> None:
    """Print legacy status message (no-flow mode)."""
    print("### Protocol Status")
    print()

    if state.decomposition_required:
        print(
            "**Note:** This task is marked as `very_complex` - "
            "decomposition is REQUIRED."
        )
    else:
        print(
            "**Note:** This task is marked as `complex` - "
            "decomposition is RECOMMENDED."
        )

    print()
    print("### Expected Behavior")
    print("1. Clarify decomposition scope (if needed)")
    print("2. Analyze task to identify decomposition axes")
    print("3. Synthesize 2+ SIMPLE subtasks with dependency graph")
    print("4. Validate decomposition (GO/NO-GO verdict)")
    print()
    print("Use without `--no-flow` to trigger agent orchestration.")


if __name__ == "__main__":
    main()
