"""
PermissionRequest hook - Sends tool permission requests to voice server

Uses the PermissionRequest hook which fires ONLY for permission requests,
providing structured payload with tool_name and tool_input.
"""

import sys
import os
import json
from pathlib import Path
from typing import Any

# Add hooks directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.tts import send_tts_request


#########################[ start format_permission_message ]#################
def format_permission_message(tool_name: str, tool_input: Any) -> str:
    """
    Format a human-readable permission message from structured tool data

    Args:
        tool_name: Name of the tool requesting permission
        tool_input: Tool input (can be dict, string, or other)

    Returns:
        Formatted message string
    """
    # Base message
    message = f"{tool_name}"

    # Add context based on tool type
    if isinstance(tool_input, dict):
        if "command" in tool_input:
            # Bash command - show truncated command
            cmd = tool_input["command"]
            if len(cmd) > 50:
                cmd = cmd[:47] + "..."
            message = f"{tool_name}: {cmd}"
        elif "file_path" in tool_input:
            # File operations - show path
            path = tool_input["file_path"]
            message = f"{tool_name}: {path}"
        elif "pattern" in tool_input:
            # Glob/Grep - show pattern
            pattern = tool_input["pattern"]
            message = f"{tool_name}: {pattern}"
        elif "url" in tool_input:
            # Web operations - show URL
            url = tool_input["url"]
            if len(url) > 40:
                url = url[:37] + "..."
            message = f"{tool_name}: {url}"
    elif isinstance(tool_input, str) and tool_input:
        # String input - show truncated
        if len(tool_input) > 50:
            tool_input = tool_input[:47] + "..."
        message = f"{tool_name}: {tool_input}"

    return message


#########################[ end format_permission_message ]###################

#########################[ start main ]######################################
def main():
    """
    Main hook function for PermissionRequest hook

    Reads structured permission payload and sends notification to voice server.
    PermissionRequest hook provides:
    - tool_name: Name of the tool requesting permission
    - tool_input: Tool input parameters (dict or other)
    - session_id: Current session ID
    - hook_event_name: "PermissionRequest"
    """
    try:
        # Read JSON payload from stdin
        hook_data = json.load(sys.stdin)

        # Extract structured data from PermissionRequest payload
        tool_name = hook_data.get('tool_name', 'Unknown')
        tool_input = hook_data.get('tool_input', {})

        # Format human-readable message from structured data
        message = format_permission_message(tool_name, tool_input)

        da_name = os.environ.get("DA_NAME", "AI Assistant")

        # Send to voice server using default "da" voice
        send_tts_request(
            f"{da_name} Permission Request: {message}",
            agent="da",
            title=f"{da_name} Permission Request",
        )

        return 0

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON payload: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"PermissionRequest hook error: {e}", file=sys.stderr)
        return 0  # Don't fail the hook even if there's an error


#########################[ end main ]########################################

if __name__ == "__main__":
    sys.exit(main())
