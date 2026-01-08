"""
PreToolUse hook for ExitPlanMode tool detection.

This hook fires when Claude invokes the ExitPlanMode tool, providing
100% reliable detection of plan mode exit without state tracking.

When triggered, creates a signal file that the Stop hook reads to
block Claude and inject the reasoning protocol directive.

Note: PreToolUse stdout goes to transcript only, NOT Claude's context.
Only Stop hooks can block and inject instructions via decision: block.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def is_subagent_session() -> bool:
    """
    Detect if running in a subagent context.
    Subagents don't use plan mode, so we skip for them.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    normalized = project_dir.replace("\\", "/")
    if "/.claude/agents/" in normalized:
        return True
    if os.environ.get("CLAUDE_AGENT_TYPE") is not None:
        return True
    return False


def find_most_recent_plan_file() -> Optional[Path]:
    """
    Find the most recently modified plan file in ~/.claude/plans/.

    Claude Code writes plan files to this directory when in plan mode.
    We find the most recent one to get the approved plan content.

    Returns:
        Path to the most recent plan file, or None if no plan files exist.
    """
    plans_dir = Path.home() / ".claude" / "plans"
    if not plans_dir.exists():
        return None

    plan_files = list(plans_dir.glob("*.md"))
    if not plan_files:
        return None

    # Sort by modification time, most recent first
    plan_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return plan_files[0]


def read_plan_file(plan_file: Path) -> Optional[str]:
    """
    Read the plan file content.

    Args:
        plan_file: Path to the plan file

    Returns:
        Plan file content as string, or None on error.
    """
    try:
        if plan_file.exists():
            return plan_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading plan file: {e}", file=sys.stderr)
    return None


def main():
    """
    Main hook function - triggers reasoning protocol on plan mode exit.

    This hook is called via PreToolUse matcher when ExitPlanMode tool is invoked.
    At this point, we KNOW plan mode is being exited - no state tracking needed.
    """
    try:
        # Read JSON payload from stdin
        hook_data = json.load(sys.stdin)

        # Skip for subagents (they don't use plan mode)
        if is_subagent_session():
            return 0

        # Get PAI_DIRECTORY for entry script path
        pai_dir = os.environ.get("PAI_DIRECTORY")
        if not pai_dir:
            print("PAI_DIRECTORY not set, cannot trigger reasoning", file=sys.stderr)
            return 0

        entry_script = Path(pai_dir) / ".claude/orchestration/protocols/reasoning/entry.py"
        if not entry_script.exists():
            print(f"entry.py not found at {entry_script}", file=sys.stderr)
            return 0

        # Find and read the most recent plan file
        plan_file = find_most_recent_plan_file()
        plan_content = ""
        plan_file_path = ""

        if plan_file:
            plan_content = read_plan_file(plan_file) or ""
            plan_file_path = str(plan_file)

        # Create signal file for Stop hook to detect
        # PreToolUse stdout goes to transcript only (NOT Claude's context)
        # Stop hook will read this and block Claude with the directive
        state_dir = Path(pai_dir) / ".claude/state"
        state_dir.mkdir(parents=True, exist_ok=True)
        signal_file = state_dir / "plan-just-exited.json"

        signal_data = {
            "plan_file": plan_file_path,
            "plan_content": plan_content,
            "timestamp": datetime.now().isoformat(),
            "entry_script": str(entry_script)
        }
        signal_file.write_text(json.dumps(signal_data, indent=2))

        return 0

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON payload: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Plan mode exit hook error: {e}", file=sys.stderr)
        return 0  # Don't fail the hook even if there's an error


if __name__ == "__main__":
    sys.exit(main())
