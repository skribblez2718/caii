"""
UserPromptSubmit Hook - Reasoning Protocol Enforcement
=======================================================

This hook executes the Mandatory Reasoning Protocol for EVERY prompt.

Supported prompt flags (can appear in any order at end of prompt):
    -i    Improve prompt via external model before processing
    -b    Bypass reasoning protocol (direct execution mode)

Examples:
    "fix the bug -b"         → Bypass reasoning, execute directly
    "add feature -i"         → Improve prompt, then run reasoning
    "refactor code -i -b"    → Improve prompt, then bypass reasoning
    "refactor code -b -i"    → Same as above (order doesn't matter)

For the main orchestrator:
    - Uses entry.py with full 8-step protocol

For Cognitive Agents (subagents):
    - Uses entry.py --agent-mode which SKIPS Step 4 (Task Routing)
    - Agents are already routed by skill orchestration

For Plan Mode:
    - Exits early (no orchestration during read-only planning)
    - The Stop hook detects plan mode exit and triggers orchestration then

For Bypass Mode (-b flag):
    - Exits early, allowing Claude to handle the prompt directly
    - Useful for trivial tasks and follow-up prompts

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


class ParsedPrompt(TypedDict):
    """Result of parsing flags from a prompt."""

    content: str    # The prompt text with flags stripped
    improve: bool   # -i flag: improve prompt via external model
    bypass: bool    # -b flag: bypass reasoning protocol


# Known prompt flags - add new flags here
# Maps flag string to attribute name in ParsedPrompt
PROMPT_FLAGS: dict[str, str] = {
    '-i': 'improve',    # Improve prompt via external model
    '-b': 'bypass',     # Bypass reasoning protocol
}


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


def parse_prompt_flags(prompt: str) -> ParsedPrompt:
    """
    Parse CLI-style flags from the end of a prompt.

    Flags can appear in any order at the end of the prompt.
    Only flags at the very end are recognized - flags embedded
    in the middle of text are treated as content.

    Examples:
        "my prompt -b"      → content="my prompt", bypass=True
        "my prompt -i -b"   → content="my prompt", improve=True, bypass=True
        "my prompt -b -i"   → content="my prompt", improve=True, bypass=True
        "my prompt"         → content="my prompt", all flags False
        "use -i flag -b"    → content="use -i flag", bypass=True

    Args:
        prompt: The raw user prompt potentially ending with flags

    Returns:
        ParsedPrompt with content and flag states
    """
    result: ParsedPrompt = {
        'content': prompt,
        'improve': False,
        'bypass': False,
    }

    # Split prompt into words and scan from the end
    words = prompt.rstrip().split()
    if not words:
        return result

    # Collect flags from the end of the prompt
    flags_found: list[str] = []
    while words and words[-1] in PROMPT_FLAGS:
        flag = words.pop()
        flags_found.append(flag)

    # Set flag states
    for flag in flags_found:
        attr_name = PROMPT_FLAGS[flag]
        result[attr_name] = True  # type: ignore[literal-required]

    # Reconstruct content without flags
    result['content'] = ' '.join(words).rstrip()

    return result


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


def handle_prompt_improvement(prompt: str, pai_dir: str) -> Tuple[bool, str]:
    """
    Handle -i flag: improve prompt via external model.

    Returns the improved prompt (or original on failure) so the caller
    can continue with normal reasoning protocol flow.

    Args:
        prompt: The user's prompt (flags already stripped by parser)
        pai_dir: CAII_DIRECTORY path for reasoning protocol

    Returns:
        Tuple of (success, prompt_to_use) - prompt_to_use is improved or original
    """
    # Attempt improvement (prompt already has flags stripped)
    improved = improve_prompt(prompt)

    if improved:
        # Success: Return improved prompt
        return (True, improved)
    else:
        # Failure: Return original prompt
        print("Prompt improvement failed, using original", file=sys.stderr)
        return (False, prompt)


def check_pending_dispatch(pai_dir: str) -> Tuple[bool, str]:
    """
    Check if there's a pending dispatch from a completed reasoning session.

    This ensures the execution chain continues even if the dispatcher
    directive printed by complete.py wasn't processed.

    Args:
        pai_dir: CAII_DIRECTORY path

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

            # Use MANDATORY_DIRECTIVE format that the orchestrator recognizes from DA.md training
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
        pai_dir: CAII_DIRECTORY path

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
    For Main Orchestrator: Uses entry.py (full 8 steps)
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

        # Get CAII_DIRECTORY early (needed for prompt improvement)
        pai_dir = os.environ.get("CAII_DIRECTORY")
        if not pai_dir:
            print("ERROR: CAII_DIRECTORY not set", file=sys.stderr)
            sys.exit(1)

        # Parse flags from prompt (order-independent)
        parsed = parse_prompt_flags(prompt)
        prompt = parsed['content']

        # Handle -i flag: improve prompt via external model
        # Works in all modes (including plan mode)
        if parsed['improve']:
            success, prompt = handle_prompt_improvement(prompt, pai_dir)
            if success:
                print(f"**Improved Prompt:**\n{prompt}\n", flush=True)

        # Handle -b flag: bypass reasoning protocol entirely
        # Exit silently - Claude sees just the clean prompt
        if parsed['bypass']:
            sys.exit(0)

        # Plan mode: exit early AFTER prompt improvement and bypass check
        # Stop hook handles triggering orchestration on plan mode exit
        if is_plan_mode(payload):
            sys.exit(0)

        # Check for pending dispatch FIRST (ensures execution chain continues)
        # Only check for main orchestrator context, not subagents
        if not is_subagent_session():
            has_pending, dispatch_directive = check_pending_dispatch(pai_dir)
            if has_pending:
                # Output the pending dispatch directive before normal reasoning
                print(dispatch_directive, flush=True)
                # Continue with normal reasoning protocol for the new prompt

        # Determine context type and set flags
        is_agent = is_subagent_session()

        # Both main orchestrator and Agent contexts use unified entry.py
        entry_script = Path(pai_dir) / ".claude/orchestration/protocols/reasoning/entry.py"
        context_type = "agent" if is_agent else "orchestrator"

        if not entry_script.exists():
            print(f"ERROR: {entry_script.name} not found: {entry_script}", file=sys.stderr)
            sys.exit(1)

        # Check for active session to resume (only for main orchestrator, not agents)
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
