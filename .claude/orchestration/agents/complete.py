"""
Agent Completion Logic

Provides common completion logic for agents.
CRITICAL: Verifies memory file exists and prints next agent directive for chaining.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from orchestration.agents.base import AgentExecutionState
from orchestration.agents.config import get_agent_config, normalize_agent_name
from orchestration.agent_chain.memory import MemoryFile, verify_memory_file_exists


def parse_args() -> argparse.Namespace:
    """Parse common arguments for agent completion."""
    parser = argparse.ArgumentParser(description="Complete agent execution")
    parser.add_argument("--state", required=True, help="Path to state file")
    parser.add_argument("--task-id", help="Task ID (overrides state)")
    parser.add_argument("--flow-id", help="Flow ID for chain continuation")
    parser.add_argument(
        "--skip-memory-check",
        action="store_true",
        help="Skip memory file verification (for testing only)",
    )
    return parser.parse_args()


def agent_complete(agent_name: str) -> None:
    """
    Common completion logic for all agents.

    This function:
    1. Loads and validates execution state
    2. Verifies memory file exists
    3. Prints completion marker
    4. Prints next agent directive (if in a flow)

    Args:
        agent_name: Name of the agent (e.g., "clarification")
    """
    args = parse_args()

    # Load state
    state = AgentExecutionState.load(Path(args.state))
    if not state:
        print(f"ERROR: Could not load state from {args.state}", file=sys.stderr)
        sys.exit(1)

    config = get_agent_config(agent_name)
    if not config:
        print(f"ERROR: Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)

    # Get task and flow IDs
    task_id = args.task_id or state.task_id
    flow_id = args.flow_id or state.flow_id

    # Verify memory file exists (unless skipped)
    if not args.skip_memory_check:
        if not verify_memory_file_exists(task_id, agent_name):
            memory_path = MemoryFile.get_path(task_id, agent_name)
            print(f"ERROR: Memory file missing: {memory_path}", file=sys.stderr)
            print(
                "Agent must write memory file before completion.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Calculate duration
    start_time = datetime.fromisoformat(state.started_at)
    end_time = datetime.now()
    duration = end_time - start_time

    # Update state
    state.metadata["completed_at"] = end_time.isoformat()
    state.metadata["duration_seconds"] = duration.total_seconds()
    state.metadata["status"] = "complete"
    state.save()

    # Print completion marker
    completion_marker = f"{agent_name.upper().replace('-', '_')}_COMPLETE"
    print(f"\n**{completion_marker}**")
    print()
    print(f"Duration: {duration.total_seconds():.1f}s")

    # If in a flow, print directive for next agent
    if flow_id:
        print()
        print("---")
        print()
        print(f"Flow `{flow_id}` continues.")
        print()
        print(
            f"**MANDATORY:** Execute the next agent in the flow "
            f"(check flow definition for `{flow_id}`)."
        )


def verify_and_complete(
    agent_name: str,
    task_id: str,
    state_path: Optional[Path] = None,
    flow_id: Optional[str] = None,
) -> bool:
    """
    Verify memory file and complete agent execution.

    Programmatic interface for agent completion.

    Args:
        agent_name: Name of the agent
        task_id: Task identifier
        state_path: Optional path to state file
        flow_id: Optional flow ID for chain continuation

    Returns:
        True if completion successful
    """
    # Verify memory file
    if not verify_memory_file_exists(task_id, agent_name):
        return False

    # Load state if path provided
    if state_path:
        state = AgentExecutionState.load(state_path)
        if state:
            state.metadata["completed_at"] = datetime.now().isoformat()
            state.metadata["status"] = "complete"
            state.save()

    return True


if __name__ == "__main__":
    # If run directly, require agent name as first argument
    if len(sys.argv) < 2:
        print(
            "Usage: python complete.py <agent_name> --state <state_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    agent = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove agent name from argv
    agent_complete(agent)
