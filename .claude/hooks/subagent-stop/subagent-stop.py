"""
SubagentStop hook - Notifies when agents complete
Parses transcript to determine which agent finished and sends completion notification
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Optional, Tuple

# Add hooks directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.tts import send_tts_request, get_voice_for_agent


#########################[ start find_agent_from_transcript ]################
def find_agent_from_transcript(transcript_path: str) -> Optional[Tuple[str, str]]:
    """
    Parse transcript to find the most recent Task tool call and extract agent info

    Args:
        transcript_path: Path to the transcript JSONL file

    Returns:
        Tuple of (agent_name, task_description) if found, None otherwise
    """
    try:
        if not os.path.exists(transcript_path):
            print(f"⚠️  Transcript file not found: {transcript_path}", file=sys.stderr)
            return None

        # Read JSONL file and collect all Task tool uses
        task_calls = []
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Look for assistant messages with tool use (use 'type' not 'role')
                    if entry.get('type') == 'assistant':
                        # Extract message object first
                        message = entry.get('message', {})
                        # Extract content from message.content
                        content = message.get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                # Check for tool_use blocks
                                if isinstance(item, dict) and item.get('type') == 'tool_use':
                                    if item.get('name') == 'Task':
                                        # Found a Task tool call
                                        tool_input = item.get('input', {})
                                        agent_name = tool_input.get('subagent_type', 'Unknown')
                                        description = tool_input.get('description', '')
                                        prompt = tool_input.get('prompt', '')

                                        # Use description if available, else first line of prompt
                                        task_desc = description if description else prompt.split('\n')[0][:100]

                                        task_calls.append((agent_name, task_desc))

                except json.JSONDecodeError:
                    continue

        # Return the most recent Task call (last one in the list)
        if task_calls:
            return task_calls[-1]

        return None

    except Exception as e:
        print(f"❌ Error parsing transcript: {e}", file=sys.stderr)
        return None


#########################[ end find_agent_from_transcript ]##################

#########################[ start generate_completion_message ]###############
def generate_completion_message(agent_name: str, task_description: str = None) -> str:
    """
    Generate a completion message for the agent

    Args:
        agent_name: The name of the agent that completed
        task_description: Optional description of what the agent was doing

    Returns:
        One-sentence completion message
    """
    # If we have a task description, use it
    if task_description and task_description.strip():
        # Clean up and truncate
        desc = task_description.strip()
        first_sentence = re.split(r'[.!?\n]', desc)[0].strip()

        if len(first_sentence) > 80:
            return f"Completed: {first_sentence[:77]}..."
        return f"Completed: {first_sentence}"

    # Generic message based on agent type
    agent_messages = {
        'general-purpose': 'Completed general task',
        'explore': 'Completed code exploration',
        'plan': 'Completed planning task',
        'research-query-decomposer': 'Completed query decomposition',
        'research-information-gatherer': 'Completed information gathering',
        'research-synthesizer': 'Completed research synthesis',
        'deliver-research': 'Completed research delivery'
    }

    return agent_messages.get(agent_name.lower(), f'Completed {agent_name} task')


#########################[ end generate_completion_message ]#################

#########################[ start main ]######################################
def main():
    """
    Main hook function
    Parses transcript to find agent and sends completion notification
    """
    try:
        # Read JSON payload from stdin
        hook_data = json.load(sys.stdin)

        # Extract transcript path
        transcript_path = hook_data.get('transcript_path')
        if not transcript_path:
            print("⚠️  No transcript_path in hook payload", file=sys.stderr)
            return 0

        # Find which agent was running by parsing transcript
        agent_info = find_agent_from_transcript(transcript_path)
        if not agent_info:
            print("⚠️  Could not determine agent from transcript", file=sys.stderr)
            return 0

        agent_name, task_description = agent_info

        # Generate completion message
        completion_message = generate_completion_message(agent_name, task_description)

        # Format agent name for display
        display_name = agent_name.capitalize()

        # Get the voice for this agent type
        voice = get_voice_for_agent(agent_name)
        print(f"🔍 Using voice: {voice} for agent type: {agent_name}", file=sys.stderr)

        # Send to voice server using the agent-specific voice
        send_tts_request(
            f"{display_name} Agent Complete: {completion_message}",
            agent=voice,
            title=f"{display_name} Agent Complete",
        )

        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON payload: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"❌ SubagentStop hook error: {e}", file=sys.stderr)
        return 0  # Don't fail the hook even if there's an error


#########################[ end main ]########################################

if __name__ == "__main__":
    sys.exit(main())
