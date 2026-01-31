"""
PreToolUse hook - Notifies when agents start
Detects Task tool calls and sends agent start notifications to voice server
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Optional

# Add hooks directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.tts import send_tts_request, get_voice_for_agent


#########################[ start generate_task_summary ]#####################
def generate_task_summary(prompt: str, description: str = None) -> str:
    """
    Generate a one-sentence task summary

    Args:
        prompt: The full task prompt
        description: Optional description parameter from Task tool

    Returns:
        One-sentence summary of the task
    """
    # If description parameter exists, use it
    if description:
        # Truncate to first sentence or 100 chars
        first_sentence = re.split(r'[.!?]', description)[0].strip()
        return first_sentence[:100]

    # Otherwise, extract from prompt
    # Try to get first line or first 100 characters
    if not prompt:
        return "Starting task"

    # Clean up the prompt
    prompt = prompt.strip()

    # Try to extract first sentence
    first_sentence = re.split(r'[.!?\n]', prompt)[0].strip()

    # Truncate to reasonable length
    if len(first_sentence) > 100:
        return first_sentence[:97] + "..."

    return first_sentence if first_sentence else "Starting task"


#########################[ end generate_task_summary ]#######################

#########################[ start main ]######################################
def main():
    """
    Main hook function
    Detects Task tool calls and sends agent start notifications
    """
    try:
        # Read JSON payload from stdin
        hook_data = json.load(sys.stdin)

        # DEBUG: Log hook firing
        print("🔍 Agent start hook fired", file=sys.stderr)
        print(f"🔍 Hook event: {hook_data.get('hook_event_name')}", file=sys.stderr)

        # Check if this is a Task tool call
        tool_name = hook_data.get('tool_name', '')
        print(f"🔍 Tool name: {tool_name}", file=sys.stderr)

        if tool_name != 'Task':
            # Not a Task tool, exit silently
            print(f"🔍 Not a Task tool, exiting silently", file=sys.stderr)
            return 0

        # Extract tool input
        tool_input = hook_data.get('tool_input', {})
        if not tool_input:
            print(f"⚠️  No tool_input in hook data", file=sys.stderr)
            return 0

        # Extract agent type (subagent_type from Task tool)
        agent_type = tool_input.get('subagent_type', 'Unknown')
        print(f"🔍 Agent type: {agent_type}", file=sys.stderr)

        # Extract task prompt and description
        prompt = tool_input.get('prompt', '')
        description = tool_input.get('description', '')

        # Generate task summary
        task_summary = generate_task_summary(prompt, description)

        # Format agent name for display
        display_name = agent_type.capitalize()

        # Get the voice for this agent type
        voice = get_voice_for_agent(agent_type)
        print(f"🔍 Using voice: {voice} for agent type: {agent_type}", file=sys.stderr)

        # Send to voice server using the agent-specific voice
        success = send_tts_request(
            f"{display_name} Agent Starting: {task_summary}",
            agent=voice,
            title=f"{display_name} Agent Starting",
        )
        print(f"🔍 Voice notification sent: {success}", file=sys.stderr)

        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON payload: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"❌ Agent start hook error: {e}", file=sys.stderr)
        return 0  # Don't fail the hook even if there's an error


#########################[ end main ]########################################

if __name__ == "__main__":
    sys.exit(main())
