"""
Flow Continuation Script

Called after agent completion to continue the agent chain.
Loads ChainState, looks up flow, prints next directive or FLOW_COMPLETE marker.

Usage:
    python3 flow_continue.py --task-id <task_id> --completed-agent <agent_name>
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

from orchestration.flow_registry import get_flow
from orchestration.agent_chain.state import ChainState
from orchestration.agent_chain.orchestrator import ChainOrchestrator


def main() -> None:
    """Continue agent flow after agent completion."""
    parser = argparse.ArgumentParser(description="Continue agent flow")
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument(
        "--completed-agent",
        required=True,
        help="Name of agent that just completed",
    )
    args = parser.parse_args()

    # Load chain state
    state = ChainState.load(args.task_id)
    if not state:
        print(f"ERROR: No chain state for task {args.task_id}", file=sys.stderr)
        sys.exit(1)

    # Look up flow
    flow = get_flow(state.flow_id)
    if not flow:
        print(f"ERROR: Unknown flow {state.flow_id}", file=sys.stderr)
        sys.exit(1)

    # Create orchestrator with existing state
    # Note: ChainOrchestrator will load existing state if same flow_id
    orchestrator = ChainOrchestrator(
        flow=flow,
        task_id=args.task_id,
        skill_name=state.skill_name,
        phase_id=state.phase_id,
    )

    # Get next directive
    next_directive = orchestrator.get_next_directive(args.completed_agent)

    if next_directive is None:
        # Flow complete - print unambiguous marker
        print()
        print(f"**FLOW_COMPLETE: {state.flow_id}**")
        print()
        print("All agents in flow have completed.")
        if state.skill_name:
            print(f"Ready for {state.skill_name} phase advancement.")
    else:
        # Print next agent directive
        print(next_directive)


if __name__ == "__main__":
    main()
