"""
UserPromptSubmit Hook - Reasoning Protocol Enforcement
=======================================================

This hook executes the Mandatory Reasoning Protocol for EVERY prompt.

For Penny (main orchestrator):
    - Uses entry.py with full 8-step protocol

For Cognitive Agents (subagents):
    - Uses entry.py --agent-mode which SKIPS Step 4 (Task Routing)
    - Agents are already routed by skill orchestration

For Plan Mode:
    - Exits early (no orchestration during read-only planning)
    - The Stop hook detects plan mode exit and triggers orchestration then

This is the ENFORCEMENT mechanism that guarantees Python orchestration runs.
"""

from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional, TextIO, Tuple, TypedDict, cast


class HookInput(TypedDict, total=False):
    """
    Typed view of the JSON object Claude Code passes to hooks.
    """

    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: str
    hook_event_name: str
    prompt: str


def _read_json_from_stdin(stdin: TextIO = sys.stdin) -> HookInput:
    """
    Read and return a JSON object from ``stdin`` as a :class:`HookInput`.
    """
    obj: Any = json.load(stdin)
    if not isinstance(obj, dict):
        raise TypeError("expected a JSON object at the top level")
    return cast(HookInput, obj)


def _extract_prompt(payload: HookInput) -> str:
    """
    Extract the ``prompt`` field from the payload.
    """
    value: Any = payload.get("prompt", "")
    return value if isinstance(value, str) else ""


def is_plan_mode(payload: HookInput) -> bool:
    """
    Detect if Claude Code is in plan mode.

    Plan mode restricts Bash execution, so we exit early and let the
    Stop hook handle triggering orchestration when plan mode exits.

    Args:
        payload: The hook input containing permission_mode

    Returns:
        True if in plan mode, False otherwise
    """
    permission_mode = payload.get("permission_mode", "")
    return permission_mode == "plan"


def is_subagent_session() -> bool:
    """
    Detect if running in a subagent context.

    Subagents are detected by:
    1. CLAUDE_PROJECT_DIR containing '/.claude/agents/' path
    2. CLAUDE_AGENT_TYPE environment variable being set

    Returns:
        True if this is a subagent session, False otherwise
    """
    # Check for agent-specific project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    normalized = project_dir.replace("\\", "/")
    if "/.claude/agents/" in normalized:
        return True

    # Check for explicit agent type marker
    if os.environ.get("CLAUDE_AGENT_TYPE") is not None:
        return True

    return False


def improve_prompt(prompt: str) -> Optional[str]:
    """
    Send prompt to OPENAI_BASE_URL/chat/completions for improvement.
    Uses OPENAI_PROMPT_IMPROVER_MODEL for the model.

    Args:
        prompt: The user's original prompt (with -i suffix already stripped)

    Returns:
        Improved prompt text, or None on failure
    """
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("OPENAI_PROMPT_IMPROVER_MODEL")

    if not base_url or not model:
        print("OPENAI_BASE_URL or OPENAI_PROMPT_IMPROVER_MODEL not set", file=sys.stderr)
        return None

    url = f"{base_url.rstrip('/')}/chat/completions"

    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"Improve the below prompt and optimize it for Claude Opus:\n\n```markdown\n{prompt}\n```"
            }
        ]
    }

    req = urllib.request.Request(url, method='POST')
    req.add_header('Content-Type', 'application/json')
    if api_key:
        req.add_header('Authorization', f'Bearer {api_key}')

    data = json.dumps(request_payload).encode('utf-8')

    # Create SSL context that doesn't verify certificates
    # User-specified OPENAI_BASE_URL is trusted (may use internal/self-signed certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        response = urllib.request.urlopen(req, data=data, timeout=180, context=ssl_context)
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip()
    except urllib.error.HTTPError as e:
        print(f"Prompt improvement HTTP error ({e.code}): {e.reason}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"Prompt improvement URL error: {e.reason}", file=sys.stderr)
    except Exception as e:
        print(f"Prompt improvement failed: {e}", file=sys.stderr)

    return None


def handle_prompt_improvement(prompt: str) -> None:
    """
    Handle -i suffix: improve prompt via external model and print to stdout.

    Simply prints the improved prompt to stdout so the user can see it
    and Claude receives it as additional context. This is the simplest
    approach recommended by Claude Code docs.

    Args:
        prompt: The user's original prompt (including -i suffix)
    """
    # Strip -i suffix
    clean_prompt = prompt.rstrip()[:-2].rstrip()

    # Attempt improvement
    improved = improve_prompt(clean_prompt)

    if improved:
        # Success: Print improved prompt to stdout
        # User sees it, Claude receives it as context
        print(improved, flush=True)
        sys.exit(0)
    else:
        # Failure: Let original prompt through (without -i suffix)
        print("Prompt improvement failed, using original", file=sys.stderr)
        sys.exit(0)


def check_pending_dispatch(pai_dir: str) -> Tuple[bool, str]:
    """
    Check if there's a pending dispatch from a completed reasoning session.

    This ensures the execution chain continues even if the dispatcher
    directive printed by complete.py wasn't processed.

    Args:
        pai_dir: PAI_DIRECTORY path

    Returns:
        Tuple of (has_pending, dispatch_directive)
    """
    # Import ProtocolState to check for pending dispatch
    state_module_path = Path(pai_dir) / ".claude/orchestration/protocols/reasoning"
    sys.path.insert(0, str(state_module_path))

    try:
        from state import ProtocolState

        state = ProtocolState.find_with_pending_dispatch()
        if state and state.dispatch_pending:
            dispatch_info = state.dispatch_pending
            directive_command = dispatch_info.get("directive_command", "")
            route = dispatch_info.get("route", "")

            # Use MANDATORY_DIRECTIVE format that Penny recognizes from her DA.md training
            directive = f"""
**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**
`{directive_command}`

⚠️ Pending dispatch from completed reasoning protocol (route: {route}).
The execution chain MUST continue. Execute this command NOW.
"""
            # Clear the pending dispatch now that we've injected it
            state.clear_dispatch_pending()
            state.save()

            return (True, directive)

    except Exception as e:
        print(f"Error checking pending dispatch: {e}", file=sys.stderr)

    return (False, "")


def check_active_session(pai_dir: str) -> Tuple[bool, str]:
    """
    Check if there's an active reasoning session awaiting clarification.

    This enables multi-turn conversations within a single reasoning session,
    specifically when:
    - Step 0 (Johari Discovery) asks clarifying questions
    - Step 8 (Knowledge Transfer) halts for clarification

    Only resumes sessions at these specific steps to avoid accidentally
    continuing an unrelated session when the user starts a new task.

    Args:
        pai_dir: PAI_DIRECTORY path

    Returns:
        Tuple of (has_active, session_id) - session_id is empty if no active session
    """
    state_module_path = Path(pai_dir) / ".claude/orchestration/protocols/reasoning"
    if str(state_module_path) not in sys.path:
        sys.path.insert(0, str(state_module_path))

    try:
        from state import ProtocolState
        from fsm import ReasoningState

        state = ProtocolState.find_active()
        if state:
            # Only resume if at clarification-eligible steps:
            # - Step 0 (JOHARI_DISCOVERY): Pre-reasoning clarification
            # - Step 8 (KNOWLEDGE_TRANSFER): Post-reasoning clarification before dispatch
            clarification_states = [
                ReasoningState.JOHARI_DISCOVERY,
                ReasoningState.KNOWLEDGE_TRANSFER,
            ]
            if state.fsm.state in clarification_states:
                return (True, state.session_id)

    except Exception as e:
        print(f"Error checking active session: {e}", file=sys.stderr)

    return (False, "")


def main() -> None:
    """
    Execute appropriate reasoning protocol entry point.

    For Plan Mode: Exits early (Stop hook handles plan mode exit triggering)
    For Penny: Uses entry.py (full 8 steps)
    For Agents: Uses entry.py --agent-mode (skips Step 4)

    The stdout becomes part of Claude's context, containing either:
    - Nothing (plan mode - handled by Stop hook on exit)
    - Directive to execute Step 1 of the reasoning protocol (normal mode)

    Exit codes:
    * ``0`` - Success
    * ``1`` - Error (message written to ``stderr``; non-blocking)
    """
    try:
        payload = _read_json_from_stdin()
        prompt = _extract_prompt(payload)

        if not prompt.strip():
            sys.exit(0)  # Empty prompt, nothing to do

        # Check for -i suffix (prompt improvement request)
        # Handled before plan mode so improvements work in any mode
        if prompt.rstrip().endswith('-i'):
            handle_prompt_improvement(prompt)
            return  # Exit after handling (handle_prompt_improvement calls sys.exit)

        # Plan mode: exit early, Stop hook handles triggering on plan mode exit
        if is_plan_mode(payload):
            sys.exit(0)

        # Get PAI_DIRECTORY from environment
        pai_dir = os.environ.get("PAI_DIRECTORY")
        if not pai_dir:
            print("ERROR: PAI_DIRECTORY not set", file=sys.stderr)
            sys.exit(1)

        # Check for pending dispatch FIRST (ensures execution chain continues)
        # Only check for Penny context, not subagents
        if not is_subagent_session():
            has_pending, dispatch_directive = check_pending_dispatch(pai_dir)
            if has_pending:
                # Output the pending dispatch directive before normal reasoning
                print(dispatch_directive, flush=True)
                # Continue with normal reasoning protocol for the new prompt

        # Determine context type and set flags
        is_agent = is_subagent_session()

        # Both Penny and Agent contexts use unified entry.py
        entry_script = Path(pai_dir) / ".claude/orchestration/protocols/reasoning/entry.py"
        context_type = "agent" if is_agent else "penny"

        if not entry_script.exists():
            print(f"ERROR: {entry_script.name} not found: {entry_script}", file=sys.stderr)
            sys.exit(1)

        # Check for active session to resume (only for Penny, not agents)
        session_to_resume = None
        if not is_agent:
            has_active, active_session_id = check_active_session(pai_dir)
            if has_active:
                session_to_resume = active_session_id

        # Build command arguments
        if session_to_resume:
            # Resume existing session instead of creating new one
            cmd_args = ["python3", str(entry_script), "--resume", session_to_resume]
        else:
            # New session with the prompt
            cmd_args = ["python3", str(entry_script), prompt]

        # Add --agent-mode flag for subagent sessions (skips Step 4)
        if is_agent:
            cmd_args.append("--agent-mode")

        # Execute entry point with the prompt
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            cwd=pai_dir,
            timeout=30,  # 30 second timeout
        )

        # Print stdout - this becomes Claude's context
        if result.stdout:
            print(result.stdout, flush=True)

        # Log stderr but don't fail the hook
        if result.stderr:
            print(f"{context_type} entry stderr: {result.stderr}", file=sys.stderr)

        sys.exit(0)

    except subprocess.TimeoutExpired:
        print("ERROR: entry script timed out after 30 seconds", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"user_prompt_submit hook error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
