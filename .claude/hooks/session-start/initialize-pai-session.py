"""
initialize-pai-session.py
=========================

Main PAI session initialization hook that runs at the start of every Claude Code
session.

What it does
------------

* Checks if this is a subagent session (skips for subagents)
* Tests that the stop-hook is properly configured
* Sets the initial terminal tab title
* Sends a voice/notification that the system is ready (if a local server is running)
* Relies on ``load-core-context.ts`` (configured elsewhere) to inject PAI context

Setup
-----

1. Set environment variables in ``settings.json``:

   - ``DA_NAME``: Your AI's name (e.g., ``"Assistant"``, ``"Kai"``, ``"Jarvis"``)
   - ``VOICE_SERVER_HOST``: Host for the voice server (defaults to ``127.0.0.1``)
   - ``VOICE_SERVER_PORT``: Port for the voice server (defaults to ``8001``)
   - ``VOICE_SERVER_API_KEY``: API key for voice server authentication
   - ``CAII_DIRECTORY``: Path to your PAI directory (defaults to ``$HOME/.claude``)

2. Ensure ``load-core-context.ts`` exists in the ``hooks/`` directory.
3. Add both hooks to ``SessionStart`` in ``settings.json``.
"""

from __future__ import annotations

import os
import stat as statmod
import sys
from pathlib import Path

# Add hooks directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.tts import send_tts_request


#########################[ start set_terminal_tab_title ]####################
def set_terminal_tab_title(title: str) -> None:
    """
    Attempt to set the terminal tab/window title using common xterm OSC sequences.

    :param title: The title string to set for the terminal/tab.
    :type title: str
    :returns: ``None``

    The function writes OSC 0, OSC 2, and OSC 30 sequences to ``stderr`` and
    flushes the stream. Not all terminals honor these sequences.
    """
    # OSC 0, OSC 2 and (less common) OSC 30
    for code in ("0", "2", "30"):
        sys.stderr.write(f"\x1b]{code};{title}\x07")
    sys.stderr.flush()


#########################[ end set_terminal_tab_title ]######################

#########################[ start test_stop_hook ]############################
def test_stop_hook() -> bool:
    """
    Validate the presence and executability of the stop-hook.

    The stop-hook is expected at ``<CAII_DIRECTORY>/.claude/hooks/stop/stop.py``.

    :returns: ``True`` if the stop-hook exists and is executable; ``False`` otherwise.
    :rtype: bool

    Behavior
    --------
    * Logs status messages to ``stderr``.
    * When the hook exists and is executable, sets the initial terminal tab
      title to ``"<DA_NAME> Ready"``.
    """
    pai_dir = os.environ.get("CAII_DIRECTORY", str(Path.home() / ".claude"))
    stop_hook_path = Path(pai_dir) / ".claude" / "hooks" / "stop" / "stop.py"

    print("\n🧪 Testing stop-hook configuration...", file=sys.stderr)

    if not stop_hook_path.exists():
        print(f"❌ Stop-hook NOT FOUND at: {stop_hook_path}", file=sys.stderr)
        return False

    try:
        # Check executable bit(s) in a POSIX-friendly way and fall back to os.access
        st_mode = stop_hook_path.stat().st_mode
        has_exec_bits = bool(
            st_mode & (statmod.S_IXUSR | statmod.S_IXGRP | statmod.S_IXOTH)
        )
        is_executable = has_exec_bits or os.access(stop_hook_path, os.X_OK)

        if not is_executable:
            print("❌ Stop-hook exists but is NOT EXECUTABLE", file=sys.stderr)
            return False

        print("✅ Stop-hook found and is executable", file=sys.stderr)

        da_name = os.environ.get("DA_NAME", "AI Assistant")
        tab_title = f"{da_name} Ready"
        set_terminal_tab_title(tab_title)
        print(f'✏️ Set initial tab title: "{tab_title}"', file=sys.stderr)
        return True
    except Exception as e:  # pragma: no cover - defensive
        print(f"❌ Error checking stop-hook: {e}", file=sys.stderr)
        return False


#########################[ end test_stop_hook ]##############################

#########################[ start is_subagent_session ]#######################
def is_subagent_session() -> bool:
    """
    Determine whether the current session is a *subagent* session.

    A session is considered a subagent if either of the following is true:

    * ``CLAUDE_PROJECT_DIR`` contains the substring ``"/.claude/agents/"``; or
    * ``CLAUDE_AGENT_TYPE`` is set in the environment.

    :returns: ``True`` if this looks like a subagent session; ``False`` otherwise.
    :rtype: bool
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    normalized = project_dir.replace("\\", "/")
    return "/.claude/agents/" in normalized or os.environ.get("CLAUDE_AGENT_TYPE") is not None


#########################[ end is_subagent_session ]#########################

#########################[ start main ]######################################
def main() -> int:
    """
    Entry point for the session start hook.

    :returns: Process exit code (``0`` for success, ``1`` for error).
    :rtype: int

    Behavior
    --------
    * Skips initialization if this is a subagent session.
    * Validates the stop-hook configuration and warns if misconfigured.
    * Sends a low-priority "systems initialized" notification (if a local
      voice/notification server is listening).
    """
    try:
        if is_subagent_session():
            print("🤖 Subagent session detected - skipping session initialization", file=sys.stderr)
            return 0

        da_name = os.environ.get("DA_NAME", "AI Assistant")
        message = f"Hey Sketch! {da_name} here. What would you like to do?"

        stop_hook_ok = test_stop_hook()
        if not stop_hook_ok:
            print(
                "\n⚠️ STOP-HOOK ISSUE DETECTED - Tab titles may not update automatically",
                file=sys.stderr,
            )

        # Note: PAI core context loading is handled by load-core-context.py hook
        # which should run BEFORE this hook in settings.json SessionStart hooks.
        send_tts_request(
            message,
            agent="da",
            title=f"{da_name} Ready",
        )

        return 0
    except Exception as e:  # pragma: no cover - defensive
        print(f"SessionStart hook error: {e}", file=sys.stderr)
        return 1


#########################[ end main ]########################################

if __name__ == "__main__":
    sys.exit(main())
