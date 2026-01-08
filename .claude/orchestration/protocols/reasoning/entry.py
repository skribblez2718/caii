"""
entry.py
========

Unified entry point for the Mandatory Reasoning Protocol.

This script supports both Penny (full 8-step) and Agent (7-step, skips Step 4) modes:

Penny Mode (default):
  All 8 steps including Step 4 (Task Routing)

Agent Mode (--agent-mode):
  Steps 1, 2, 3, 5, 6, 7, 8 (skips Step 4 since agents are already routed)

Usage:
    python entry.py "user query here"
    python entry.py --resume <session_id>
    python entry.py "agent task" --agent-mode

The stdout from this script becomes part of Claude's context,
instructing it to proceed with the reasoning protocol.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Path setup - add protocols directory for fully-qualified imports
# This prevents collision between reasoning/config and skill/config
_REASONING_ROOT = Path(__file__).resolve().parent
_PROTOCOLS_DIR = _REASONING_ROOT.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

from reasoning.config.config import (
    ORCHESTRATION_ROOT,
    STEPS_DIR,
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    STEP_NAMES,
    STEP_TITLES,
    ensure_directories,
    format_mandatory_directive,
)
from reasoning.core.state import ProtocolState


# Step sequences for different modes
# Step 0 (Johari Discovery) executes at START of every interaction
FULL_STEP_SEQUENCE = [0, 1, 2, 3, 4, 5, 6, 7, 8]
AGENT_STEP_SEQUENCE = [0, 1, 2, 3, 5, 6, 7, 8]  # Skips Step 4 (Task Routing)


def get_step_sequence(is_agent_mode: bool) -> list[int]:
    """
    Get the step sequence for the given mode.

    Args:
        is_agent_mode: True for agent mode (skips Step 4)

    Returns:
        List of step numbers to execute
    """
    return AGENT_STEP_SEQUENCE if is_agent_mode else FULL_STEP_SEQUENCE


def get_next_step(current_step: int, is_agent_mode: bool) -> int | None:
    """
    Get the next step in the sequence.

    For agents, we skip Step 4 (Task Routing) since they're already routed.

    Args:
        current_step: The current step number
        is_agent_mode: True if running in agent mode

    Returns:
        Next step number, or None if protocol complete
    """
    sequence = get_step_sequence(is_agent_mode)
    try:
        current_idx = sequence.index(current_step)
        if current_idx + 1 < len(sequence):
            return sequence[current_idx + 1]
        return None  # Protocol complete
    except ValueError:
        # Step not in sequence - find nearest next step
        for step in sequence:
            if step > current_step:
                return step
        return None


def print_protocol_preamble(state: ProtocolState, is_agent_mode: bool = False) -> None:
    """
    Print the protocol preamble to stdout.

    This becomes part of Claude's context, establishing the
    deterministic execution framework.

    Args:
        state: The protocol state
        is_agent_mode: True if running in agent mode
    """
    if is_agent_mode:
        print(f"Agent Task: {state.user_query}")
        print("\n[AGENT REASONING MODE: Step 4 (Task Routing) will be skipped - agent already routed]")
    else:
        # Query context only - protocol rules are in step markdown files
        print(f"Query: {state.user_query}")


def print_step_directive(state: ProtocolState, step_num: int = 1, is_agent_mode: bool = False) -> None:
    """
    Print the directive to execute a specific step.

    This is the key mechanism: printing the command that Claude
    should execute to proceed with the protocol.

    Args:
        state: The protocol state
        step_num: The step number to execute
        is_agent_mode: True if running in agent mode
    """
    step_name = STEP_NAMES.get(step_num, "unknown").lower()
    script_path = STEPS_DIR / f"step_{step_num}_{step_name}.py"
    state_file = state.state_file_path

    if is_agent_mode:
        # Note the agent context in the directive
        sequence = AGENT_STEP_SEQUENCE
        step_position = sequence.index(step_num) + 1 if step_num in sequence else step_num
        total_agent_steps = len(sequence)

        directive = format_mandatory_directive(
            f"python3 {script_path} --state {state_file}",
            f"Agent reasoning step {step_position} of {total_agent_steps}. Step 4 (routing) is skipped for agents. "
        )
    else:
        # Step 0 has special wording, Steps 1-8 use standard wording
        if step_num == 0:
            step_context = "This is Step 0 (Johari Discovery). Execute at START of every interaction. "
        else:
            step_context = f"This is Step {step_num} of 8. Each step's output feeds into the next. "
        directive = format_mandatory_directive(
            f"python3 {script_path} --state {state_file}",
            step_context
        )
    print(directive)


def init_protocol(user_query: str, is_agent_mode: bool = False) -> ProtocolState:
    """
    Initialize a new protocol session.

    Args:
        user_query: The user's original query
        is_agent_mode: If True, run in agent mode (skip Step 4)

    Returns:
        Initialized ProtocolState
    """
    ensure_directories()

    state = ProtocolState(user_query=user_query)

    # Set agent mode metadata
    if is_agent_mode:
        state.metadata["is_agent_session"] = True
        state.metadata["skip_step_4"] = True
        state.metadata["step_sequence"] = AGENT_STEP_SEQUENCE

    state.save()

    return state


def resume_protocol(session_id: str) -> ProtocolState | None:
    """
    Resume an existing protocol session.

    Args:
        session_id: The session ID to resume

    Returns:
        Restored ProtocolState or None if not found
    """
    return ProtocolState.load(session_id)


def main() -> int:
    """
    Main entry point for the protocol.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Initiate the Mandatory Reasoning Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Penny mode (full 8-step protocol)
  python entry.py "How do I implement authentication?"
  python entry.py --resume abc123def456

  # Agent mode (skips Step 4 - task routing)
  python entry.py "Clarify OAuth2 requirements" --agent-mode
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="The user query to process through the protocol"
    )
    parser.add_argument(
        "--resume",
        metavar="SESSION_ID",
        help="Resume an existing protocol session"
    )
    parser.add_argument(
        "--agent-mode",
        action="store_true",
        help="Run in agent mode (skips Step 4 - task routing). Use for cognitive agents."
    )

    args = parser.parse_args()

    # Handle resume
    if args.resume:
        state = resume_protocol(args.resume)
        if not state:
            print(f"ERROR: Session {args.resume} not found", file=sys.stderr)
            return 1

        if state.fsm.is_final():
            print(f"Session {args.resume} has already completed.", file=sys.stderr)
            return 1

        # Determine mode from state metadata or command line
        is_agent_mode = args.agent_mode or state.metadata.get("is_agent_session", False)

        # Resume from current or next step
        current_step = state.current_step
        if current_step is not None:
            # Check if current step is already completed
            step_key = str(int(current_step))
            timestamps = state.step_timestamps.get(int(current_step)) or state.step_timestamps.get(step_key, {})
            step_completed = timestamps.get("completed_at") is not None

            if step_completed:
                # Current step finished, move to next step
                next_step = get_next_step(int(current_step), is_agent_mode)
                if next_step is not None:
                    print_step_directive(state, next_step, is_agent_mode=is_agent_mode)
                else:
                    # Protocol complete, nothing to do
                    print("Protocol already completed.")
            else:
                # Step in progress, resume it
                # If we're at step 4 in an agent session, skip to step 5
                if current_step == 4 and is_agent_mode:
                    current_step = 5
                print_step_directive(state, int(current_step), is_agent_mode=is_agent_mode)
        else:
            # Protocol just initialized, start at step 0 (Johari Discovery)
            print_protocol_preamble(state, is_agent_mode=is_agent_mode)
            print_step_directive(state, 0, is_agent_mode=is_agent_mode)

        return 0

    # Require query for new session
    if not args.query:
        parser.print_help()
        print("\nERROR: Query required for new session", file=sys.stderr)
        return 1

    # Initialize new protocol
    state = init_protocol(
        args.query,
        is_agent_mode=args.agent_mode
    )

    # Print preamble and first step directive (Step 0 - Johari Discovery)
    print_protocol_preamble(state, is_agent_mode=args.agent_mode)
    print_step_directive(state, 0, is_agent_mode=args.agent_mode)

    return 0


if __name__ == "__main__":
    sys.exit(main())
