"""
Common Skill Completion Logic
=============================

Shared completion logic for all composite skills.
Each skill's complete.py imports and calls skill_complete().

Integrates with episodic memory to store episodes after each skill completion.
Triggers automatic state cleanup when skills reach FULLY_COMPLETE.
All imports are ABSOLUTE - no relative imports allowed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Path setup - add protocols directory for fully-qualified imports
# This prevents collision between skill/config and agent/config
# From composite/common_skill_complete.py, go up 2 levels to reach protocols/
_COMPOSITE_DIR = Path(__file__).resolve().parent
_SKILL_PROTOCOLS_ROOT = _COMPOSITE_DIR.parent
_PROTOCOLS_DIR = _SKILL_PROTOCOLS_ROOT.parent
_ORCHESTRATION_ROOT = _PROTOCOLS_DIR.parent
_CLAUDE_ROOT = _ORCHESTRATION_ROOT.parent

if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

# Fully-qualified imports from skill package
from skill.core.state import SkillExecutionState
from skill.core.fsm import SkillPhaseState
from skill.memory_verifier import list_memory_files, verify_format
from skill.episode_store_helper import store_skill_episode, create_episode_from_skill_state
from skill.learning_trigger import should_trigger_learnings, format_trigger_prompt
from skill.episodic_memory import load_all_episodes

# Skills that bypass mandatory learnings capture
# for performance optimization or to prevent recursion
SKILLS_BYPASSING_LEARNINGS = frozenset([
    "develop-learnings",  # Prevent recursion
])


def _trigger_cleanup() -> int:
    """
    Trigger state cleanup after task completion.

    Removes all state JSON files from orchestration directories
    and all memory markdown files.

    Returns:
        Number of files cleaned (0 if cleanup failed)
    """
    try:
        # Build cleanup commands
        cleanup_commands = [
            # Remove all state JSON files
            f'find {_ORCHESTRATION_ROOT} -path "*/state/*.json" -type f -delete',
            # Remove all memory markdown files
            f'find {_CLAUDE_ROOT}/memory -name "*.md" -type f -delete 2>/dev/null || true',
        ]

        cleaned = 0

        # Count files before deletion
        count_state = subprocess.run(
            f'find {_ORCHESTRATION_ROOT} -path "*/state/*.json" -type f | wc -l',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        count_memory = subprocess.run(
            f'find {_CLAUDE_ROOT}/memory -name "*.md" -type f 2>/dev/null | wc -l',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

        try:
            cleaned += int(count_state.stdout.strip())
            cleaned += int(count_memory.stdout.strip())
        except ValueError:
            pass

        # Execute cleanup
        for cmd in cleanup_commands:
            subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=30,
            )

        return cleaned
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return 0


def parse_args() -> argparse.Namespace:
    """Parse common arguments for skill completion."""
    parser = argparse.ArgumentParser(description="Complete skill execution")
    parser.add_argument("session_id", help="Session ID")
    return parser.parse_args()


def _extract_episode_data(state: SkillExecutionState, skill_name: str) -> dict:
    """
    Extract episode data from skill execution state.

    Args:
        state: The skill execution state
        skill_name: Name of the completed skill

    Returns:
        Dictionary with episode data fields
    """
    # Extract task description from metadata or generate from task_id
    task_description = state.metadata.get(
        "task_description",
        state.metadata.get("original_request", f"Task {state.task_id}")
    )

    # Extract domain from metadata
    domain = state.metadata.get("domain", "technical")

    # Extract agents invoked from metadata or phase history
    agents_invoked = state.metadata.get("agents_invoked", [])

    # If no agents tracked, try to infer from phases
    if not agents_invoked and hasattr(state, "phase_history"):
        agents_invoked = [
            phase.get("agent", "unknown")
            for phase in state.phase_history
            if phase.get("agent")
        ]

    # Determine outcome based on status
    status = state.metadata.get("status", "complete")
    if status == "complete":
        outcome = "success"
    elif status == "partial":
        outcome = "partial"
    else:
        outcome = "failure"

    return {
        "task_id": state.task_id,
        "skill_name": skill_name,
        "task_description": task_description,
        "domain": domain,
        "agents_invoked": agents_invoked,
        "outcome": outcome,
    }


def _store_completion_episode(state: SkillExecutionState, skill_name: str):
    """
    Store an episode in episodic memory after skill completion.

    Extracts relevant information from the skill execution state
    and stores it for future pattern matching and recommendations.

    Args:
        state: The skill execution state
        skill_name: Name of the completed skill

    Returns:
        Tuple of (episode_id, episode) for further analysis
    """
    data = _extract_episode_data(state, skill_name)

    # Create the episode object for analysis
    episode = create_episode_from_skill_state(
        task_id=data["task_id"],
        skill_name=data["skill_name"],
        task_description=data["task_description"],
        domain=data["domain"],
        agents_invoked=data["agents_invoked"],
        outcome=data["outcome"],
    )

    # Store the episode
    episode_id = store_skill_episode(
        task_id=data["task_id"],
        skill_name=data["skill_name"],
        task_description=data["task_description"],
        domain=data["domain"],
        agents_invoked=data["agents_invoked"],
        outcome=data["outcome"],
    )

    return episode_id, episode


def skill_complete(skill_name: str) -> None:
    """
    Common completion logic for composite skills.

    Validates FSM state, checks memory files, outputs summary.

    Args:
        skill_name: Name of the skill (e.g., "develop-skill")
    """
    args = parse_args()

    state = SkillExecutionState.load(skill_name, args.session_id)
    if not state:
        print(f"ERROR: State not found for session {args.session_id}", file=sys.stderr)
        sys.exit(1)

    # Verify FSM completion
    # NOTE: FSM stores state as SkillPhaseState enum in .state attribute, not .current_state
    if state.fsm and state.fsm.state != SkillPhaseState.COMPLETED:
        print(f"WARNING: FSM state is {state.fsm.state.name}, not COMPLETED", file=sys.stderr)

    # Check memory files
    memory_files = list_memory_files(state.task_id)
    valid_count = sum(1 for mf in memory_files if verify_format(mf)[0])

    # Calculate duration
    start_time = datetime.fromisoformat(state.started_at)
    duration = datetime.now() - start_time

    # Update state
    state.metadata["completed_at"] = datetime.now().isoformat()
    state.metadata["duration_seconds"] = duration.total_seconds()
    state.metadata["status"] = "complete"
    state.save()

    # Store episode in episodic memory
    episode_id, episode = _store_completion_episode(state, skill_name)

    # Minimal output
    print(f"## {skill_name} Complete")
    print(f"Task: `{state.task_id[:20]}...`")
    print(f"Duration: {duration.total_seconds():.1f}s")
    print(f"Memory files: {valid_count}/{len(memory_files)}")
    print(f"Episode stored: `{episode_id}`")
    print()
    print(f"**{skill_name.upper().replace('-', '_')}_COMPLETE**")
    print()

    # ENFORCEMENT: Mandatory learnings capture
    # Skip for skills in bypass list (prevent recursion or for performance)
    if skill_name not in SKILLS_BYPASSING_LEARNINGS:
        # Transition FSM to LEARNINGS_PENDING state
        if state.fsm:
            state.fsm.require_learnings()
            state.save()

        # Build the develop-learnings command
        learnings_entry = Path(__file__).parent / "develop_learnings" / "entry.py"
        learnings_task_id = f"learnings-{state.task_id[:8]}"
        learnings_command = f"python3 {learnings_entry} {learnings_task_id} --source-task {state.task_id}"

        print()
        print("=" * 70)
        print("# MANDATORY: Learnings Capture Required")
        print("=" * 70)
        print()
        print("This workflow has completed all phases. Learnings MUST be captured")
        print("before the workflow is considered FULLY COMPLETE.")
        print()
        print("## Why This Matters")
        print()
        print("- Unknown unknowns resolved during this workflow become permanent knowledge")
        print("- Patterns and anti-patterns are preserved for future use")
        print("- Cognitive agents improve with each captured learning")
        print()
        print("Learnings are organized by cognitive function and stored in:")
        print("`${PAI_DIRECTORY}/.claude/learnings/{function}/`")
        print()
        print("=" * 70)
        print()
        print("**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**")
        print(f"`{learnings_command}`")
        print()
        print("⚠️ DO NOT proceed with any other action until this command is executed.")
        print("The develop-learnings skill will capture insights from the completed workflow.")
        print()
        print("=" * 70)
        print(f"**STATUS:** LEARNINGS_PENDING (not fully complete)")
        print("=" * 70)
        print()
    else:
        # For bypassed skills, mark as fully complete
        if state.fsm:
            # These skills don't need to capture learnings
            state.fsm.state = SkillPhaseState.FULLY_COMPLETE
            state.fsm.history.append("FULLY_COMPLETE")
            state.save()

        # Trigger automatic state cleanup
        cleaned = _trigger_cleanup()

        print()
        print("=" * 70)
        print(f"**STATUS:** FULLY_COMPLETE")
        if cleaned > 0:
            print(f"**CLEANUP:** {cleaned} old state files removed")
        print("=" * 70)
        print()
