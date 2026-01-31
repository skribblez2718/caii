"""
scaffold-docs Skill Entry Point

Main entry point for scaffold-docs skill. Creates or loads state
and routes to appropriate flow based on mode (scaffold vs update).
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

from orchestration.skills.scaffold_docs.scaffold_docs_state import (
    ScaffoldDocsPhase,
    ScaffoldDocsState,
)
from orchestration.skills.scaffold_docs.flows import get_flow_for_mode
from orchestration.skills.scaffold_docs.detector import detect_language
from orchestration.agent_chain.orchestrator import ChainOrchestrator

# Content directory for agent-specific content
CONTENT_DIR = Path(__file__).parent / "content"


def determine_mode(target_path: Path) -> str:
    """
    Determine operation mode based on existing documentation.

    Args:
        target_path: Path to target project directory

    Returns:
        'scaffold' if no CLAUDE.md exists, 'update' otherwise
    """
    claude_md = target_path / "CLAUDE.md"
    if claude_md.exists():
        return "update"
    return "scaffold"


def main() -> None:
    """Main entry point for scaffold-docs skill."""
    parser = argparse.ArgumentParser(description="scaffold-docs Skill Entry Point")
    parser.add_argument(
        "--algorithm-state",
        required=True,
        help="Parent algorithm session ID",
    )
    parser.add_argument(
        "--scaffold-docs-state",
        help="Existing scaffold-docs session ID to resume",
    )
    parser.add_argument(
        "--target",
        help="Target project directory path",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Force update mode (skip clarification)",
    )
    args = parser.parse_args()

    # Resolve target path
    if args.target:
        target_path = Path(args.target).resolve()
    else:
        # Use PROJECT_ROOT from environment, fallback to cwd
        import os

        project_root = os.environ.get("PROJECT_ROOT", str(Path.cwd()))
        target_path = Path(project_root).resolve()

    # Verify target exists
    if not target_path.exists():
        print(f"ERROR: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    if not target_path.is_dir():
        print(f"ERROR: Target path is not a directory: {target_path}", file=sys.stderr)
        sys.exit(1)

    # Load or create state
    if args.scaffold_docs_state:
        state = ScaffoldDocsState.load(args.scaffold_docs_state)
        if not state:
            print(
                f"ERROR: scaffold-docs session {args.scaffold_docs_state} not found",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Determine mode
        if args.update:
            mode = "update"
        else:
            mode = determine_mode(target_path)

        state = ScaffoldDocsState(
            parent_algorithm_id=args.algorithm_state,
            target_path=str(target_path),
            mode=mode,
        )

        # Detect language
        language_info = detect_language(target_path)
        state.detected_language = language_info.language

    # Get starting phase based on mode
    if state.current_phase == ScaffoldDocsPhase.INITIALIZED:
        if state.mode == "update":
            state.advance_to_phase(ScaffoldDocsPhase.ANALYSIS)
        else:
            state.advance_to_phase(ScaffoldDocsPhase.CLARIFICATION)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Get current phase
    current_phase = state.current_phase

    # Check if completed
    if current_phase == ScaffoldDocsPhase.COMPLETED:
        print("Documentation scaffolding completed.")
        _print_summary(state)
        return

    # Print header
    print(f"## scaffold-docs {state.mode.upper()} Mode")
    print()
    print(f"**Session:** {state.session_id}")
    print(f"**Target:** {state.target_path}")
    print(f"**Language:** {state.detected_language or 'unknown'}")
    print(f"**Phase:** {current_phase.name}")
    print()

    # Get flow for mode
    try:
        flow = get_flow_for_mode(state.mode)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Build task description
    task_description = f"scaffold-docs {state.mode} for {state.target_path}"

    # Create orchestrator and start flow
    orchestrator = ChainOrchestrator(
        flow=flow,
        task_id=state.session_id,
        skill_content_dir=CONTENT_DIR,
        skill_name="scaffold-docs",
        phase_id=state.mode,
        domain="technical",
        task_description=task_description,
    )

    # Print flow info
    print("---")
    print()
    print(f"**Flow:** {flow.name} (`{flow.flow_id}`)")
    print(f"**Agents:** {' → '.join(s.agent_name for s in flow.steps)}")
    print()

    # Start the flow
    directive = orchestrator.start_flow()
    print(directive)


def _print_summary(state: ScaffoldDocsState) -> None:
    """Print completion summary."""
    print()
    print("### Summary")
    print()

    if state.created_files:
        print("**Created files:**")
        for f in state.created_files:
            print(f"- {f}")
        print()

    if state.updated_files:
        print("**Updated files:**")
        for f in state.updated_files:
            print(f"- {f}")
        print()


if __name__ == "__main__":
    main()
