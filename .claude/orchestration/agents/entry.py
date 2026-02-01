"""
Agent Entry Point Logic

Provides common entry point logic for agent execution.
"""

import argparse
import sys
import uuid
from pathlib import Path

from orchestration.agents.base import AgentExecutionState
from orchestration.agents.config import get_agent_config


def parse_args(agent_name: str) -> argparse.Namespace:
    """
    Parse common arguments for agent entry.

    Args:
        agent_name: Name of the agent

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description=f"Initialize {agent_name} execution")
    parser.add_argument("task_id", nargs="?", default=None, help="Task ID")
    parser.add_argument("--skill-name", help="Skill name if invoked from a skill")
    parser.add_argument("--phase-id", help="Phase ID if invoked from a skill")
    parser.add_argument("--flow-id", help="Flow ID if part of an agent chain")
    parser.add_argument(
        "--context-pattern",
        default="IMMEDIATE_PREDECESSORS",
        choices=["WORKFLOW_ONLY", "IMMEDIATE_PREDECESSORS", "MULTIPLE_PREDECESSORS"],
        help="Context loading pattern",
    )
    parser.add_argument(
        "--predecessors",
        help="Comma-separated list of predecessor agent names",
    )
    return parser.parse_args()


def agent_entry(agent_name: str) -> None:
    """
    Common entry point logic for all agents.

    Args:
        agent_name: Name of the agent (e.g., "clarification")
    """
    args = parse_args(agent_name)

    task_id = args.task_id or str(uuid.uuid4())[:12]
    config = get_agent_config(agent_name)

    if not config:
        print(f"ERROR: Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)

    # Create execution state
    state = AgentExecutionState(
        agent_name=agent_name,
        task_id=task_id,
        current_step=1,
    )

    # Store skill context if provided
    predecessors = args.predecessors.split(",") if args.predecessors else []
    state.set_skill_context(
        skill_name=args.skill_name,
        phase_id=args.phase_id,
        flow_id=args.flow_id,
        context_pattern=args.context_pattern,
        predecessors=predecessors,
    )

    # Save state BEFORE printing directive
    state.save()

    # Print header
    print(f"## {config['cognitive_function']} Agent")
    print(f"Task: `{task_id}`")
    if args.skill_name:
        print(f"Skill: `{args.skill_name}` | Phase: `{args.phase_id or 'N/A'}`")
    if args.flow_id:
        print(f"Flow: `{args.flow_id}`")
    print()

    # Print state file location
    print(f"State file: `{state.state_file_path}`")
    print()

    # Ready for work
    print("---")
    print()
    print("**Agent initialized. Proceed with cognitive work.**")


def get_state_path(agent_name: str, task_id: str) -> Path:
    """
    Get the path to an agent's state file.

    Args:
        agent_name: Agent name
        task_id: Task identifier

    Returns:
        Path to state file
    """
    from orchestration.agents.base import AGENT_STATE_DIR

    return AGENT_STATE_DIR / f"{agent_name}-{task_id}.json"


if __name__ == "__main__":
    # If run directly, require agent name as first argument
    if len(sys.argv) < 2:
        print(
            "Usage: python entry.py <agent_name> [task_id] [options]", file=sys.stderr
        )
        sys.exit(1)

    agent = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove agent name from argv
    agent_entry(agent)
