"""
Entry Point Base Module

Provides reusable infrastructure for orchestration entry points.
Follows Single Responsibility: each function does ONE thing.

Supports two modes:
1. Legacy mode: Load static content from markdown files
2. Agent flow mode: Trigger agent chains via ChainOrchestrator
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.state import AlgorithmState
    from orchestration.agent_chain.flow import AgentFlow

from orchestration.state.algorithm_fsm import AlgorithmPhase


@dataclass(frozen=True)
class PhaseConfig:
    """
    Immutable configuration for a phase entry point.

    Attributes:
        phase: AlgorithmPhase enum for FSM transitions
        phase_name: Human-readable name (e.g., "OBSERVE") for display/logging
        content_file: Markdown file in content/ directory (used in legacy mode)
        description: Argparse description string
        extra_placeholders: Optional callable(state) -> dict for additional substitutions
        agent_flow: Optional AgentFlow for phases using agent orchestration
        skill_name: Skill name for agent flow mode
        skill_content_dir: Path to skill's content directory for agent flow mode
    """

    phase: AlgorithmPhase
    phase_name: str
    content_file: str
    description: str
    extra_placeholders: Optional[Callable[["AlgorithmState"], Dict[str, Any]]] = None
    # Agent flow support
    agent_flow: Optional["AgentFlow"] = None
    skill_name: Optional[str] = None
    skill_content_dir: Optional[Path] = None


def load_state_or_exit(session_id: str) -> "AlgorithmState":
    """
    Load algorithm state or exit with error.

    Single Responsibility: State loading with standard error handling.

    Args:
        session_id: The session identifier to load

    Returns:
        Loaded AlgorithmState instance

    Raises:
        SystemExit: If state not found (exits with code 1)
    """
    from orchestration.state import AlgorithmState

    state = AlgorithmState.load(session_id)
    if not state:
        print(f"ERROR: Session {session_id} not found", file=sys.stderr)
        sys.exit(1)
    return state


def start_phase_or_exit(
    state: "AlgorithmState",
    phase: AlgorithmPhase,
    phase_name: str,
) -> None:
    """
    Start phase or exit with error.

    Single Responsibility: Phase transition with standard error handling.

    Args:
        state: The AlgorithmState to transition
        phase: The AlgorithmPhase enum to transition to
        phase_name: Human-readable phase name for error messages

    Raises:
        SystemExit: If transition fails (exits with code 1)
    """
    if not state.start_phase(phase):
        print(f"ERROR: Cannot transition to {phase_name} phase", file=sys.stderr)
        print(f"Current phase: {state.current_phase.name}", file=sys.stderr)
        sys.exit(1)


def create_phase_parser(description: str) -> argparse.ArgumentParser:
    """
    Create standard argument parser for phase entry points.

    Single Responsibility: Parser creation with standard arguments.

    Args:
        description: Description string for the parser

    Returns:
        Configured ArgumentParser with --state and user_query arguments
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--state", required=True, help="Session ID for state tracking")
    parser.add_argument("user_query", nargs="?", default="", help="User query (legacy)")
    return parser


def run_phase_entry(
    caller_file: str,
    config: PhaseConfig,
    argv: Optional[List[str]] = None,
) -> None:
    """
    Run a standard phase entry point.

    Orchestrates the complete phase lifecycle:
    1. Parse arguments
    2. Load state
    3. Transition to phase
    4. Save state (CRITICAL: before output)
    5. Either invoke agent flow OR load static content

    Args:
        caller_file: Pass __file__ from calling script
        config: PhaseConfig defining phase behavior
        argv: Optional argv override for testing
    """
    from orchestration.utils import load_content, substitute_placeholders

    # Parse arguments
    parser = create_phase_parser(config.description)
    args = parser.parse_args(argv)

    # Load state
    state = load_state_or_exit(args.state)

    # Start phase
    start_phase_or_exit(state, config.phase, config.phase_name)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # NEW: If agent flow is configured, use flow invocation
    if config.agent_flow:
        from orchestration.flow_invoker import (
            invoke_agent_flow,
            get_flow_directive_info,
        )

        # Build task description
        task_description = f"{config.phase_name} phase"

        # Print flow info header
        print(f"## {config.phase_name} Phase")
        print()
        print(f"**Session:** {state.session_id}")
        print()
        print(get_flow_directive_info(config.agent_flow))
        print()

        # Invoke the agent flow
        directive = invoke_agent_flow(
            flow=config.agent_flow,
            task_id=state.session_id,
            skill_name=config.skill_name or config.phase_name.lower(),
            phase_id=config.phase_name.lower(),
            skill_content_dir=config.skill_content_dir,
            task_description=task_description,
        )
        print(directive)
        return

    # LEGACY: Load and print static content
    content = load_content(caller_file, config.content_file)

    # Build placeholders
    placeholders: Dict[str, Any] = {
        "user_query": state.user_query,
        "session_id": state.session_id,
    }

    # Add extra placeholders if configured
    if config.extra_placeholders:
        placeholders.update(config.extra_placeholders(state))

    # Output
    prompt = substitute_placeholders(content, **placeholders)
    print(prompt)
