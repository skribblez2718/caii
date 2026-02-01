"""
Shared TTS utilities for Claude Code hooks.

Provides centralized TTS functionality for the caii-voice-server:
- WAV audio format (server returns WAV, not MP3)
- X-API-Key authentication header
- Agent-to-voice mapping for multi-voice support
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from typing import Optional


# Agent type to voice mapping
# Maps Claude Code agent types to caii-voice-server voice names
AGENT_VOICE_MAP: dict[str, str] = {
    # Direct matches
    "analysis": "analysis",
    "clarification": "clarification",
    "memory": "memory",
    "research": "research",
    "synthesis": "synthesis",
    # Mapped types
    "validation": "verification",  # validation -> verification
    # Default voice for other agent types
    "explore": "da",
    "plan": "da",
    "general-purpose": "da",
    "generation": "da",
    "bash": "da",
}

# Voice names available on the server
AVAILABLE_VOICES: set[str] = {
    "da", "analysis", "clarification", "memory",
    "research", "synthesis", "verification"
}


def get_voice_for_agent(agent_type: str) -> str:
    """
    Map agent type to voice name.

    Args:
        agent_type: The agent type from Task tool (e.g., "analysis", "Explore", "validation")

    Returns:
        Voice name for the caii-voice-server (e.g., "analysis", "da", "verification")
    """
    # Normalize to lowercase for lookup
    normalized = agent_type.lower() if agent_type else "da"

    # If it's already a valid voice name, return it directly
    if normalized in AVAILABLE_VOICES:
        return normalized

    # Look up in the mapping, default to "da"
    return AGENT_VOICE_MAP.get(normalized, "da")


def play_audio(audio_file: str) -> bool:
    """
    Play WAV audio file using available Linux audio players.

    Priority order:
    1. aplay - ALSA native WAV support (best for WAV)
    2. paplay - PulseAudio native WAV support
    3. mpv - Universal player
    4. ffplay - FFmpeg player

    Args:
        audio_file: Path to the WAV audio file

    Returns:
        True if playback successful, False otherwise
    """
    # Players that support WAV natively (preferred for WAV files)
    audio_players = [
        ["aplay", "-q"],  # ALSA - native WAV, quiet mode
        ["paplay"],       # PulseAudio - native WAV
        ["mpv", "--no-video", "--really-quiet"],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
    ]

    for player_cmd in audio_players:
        try:
            cmd = player_cmd + [audio_file]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            print(f"[tts] Audio player not found: {player_cmd[0]}", file=sys.stderr)
            continue
        except subprocess.TimeoutExpired:
            print(f"[tts] Audio playback timed out with {player_cmd[0]}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"[tts] Audio player {player_cmd[0]} failed: {e}", file=sys.stderr)
            continue

    print("[tts] ERROR: No audio player available (tried: aplay, paplay, mpv, ffplay)", file=sys.stderr)
    return False


def send_tts_request(
    text: str,
    agent: str = "da",
    title: Optional[str] = None,
    send_desktop_notification: bool = True,
) -> bool:
    """
    Send TTS request to caii-voice-server and play the audio.

    Args:
        text: Text to speak (the main message content)
        agent: Voice name OR agent type (will be mapped to voice if needed)
        title: Optional title for desktop notification (defaults to DA_NAME)
        send_desktop_notification: Whether to also send a desktop notification

    Returns:
        True if successful, False otherwise

    Environment Variables:
        VOICE_SERVER_PROTOCOL: Protocol for voice server (default: http)
        VOICE_SERVER_HOST: Host for voice server (default: 127.0.0.1)
        VOICE_SERVER_PORT: Port for voice server (default: 8001)
        VOICE_SERVER_API_KEY: API key for authentication
        DA_NAME: Assistant name for notifications
    """
    protocol = os.environ.get("VOICE_SERVER_PROTOCOL", "http")
    host = os.environ.get("VOICE_SERVER_HOST", "127.0.0.1")
    port = os.environ.get("VOICE_SERVER_PORT", "8001")
    api_key = os.environ.get("VOICE_SERVER_API_KEY", "")
    da_name = os.environ.get("DA_NAME", "AI Assistant")

    # Map agent type to voice if it's not already a valid voice name
    voice = get_voice_for_agent(agent)

    try:
        url = f"{protocol}://{host}:{port}/v1/audio/speech"
        print(f"[tts] Sending request to {url} (voice={voice})", file=sys.stderr)

        payload = {
            "input": text,
            "agent": voice,
            "response_format": "wav",
        }

        # Build headers with auth
        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["X-API-Key"] = api_key

        # Create request
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        # Send request
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                print(f"Voice server responded with status {response.status}", file=sys.stderr)
                return False

            # Read audio data
            audio_data = response.read()

            # Save to temp file with .wav extension
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                audio_file = f.name

            try:
                # Play the audio
                played = play_audio(audio_file)

                # Send desktop notification if requested
                if send_desktop_notification:
                    notification_title = title or da_name
                    try:
                        subprocess.run(
                            ["notify-send", notification_title, text],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=5,
                        )
                    except Exception:
                        pass

                if played:
                    return True
                else:
                    print("Audio generated but playback failed", file=sys.stderr)
                    return False

            finally:
                # Clean up temp file
                try:
                    os.unlink(audio_file)
                except Exception:
                    pass

    except urllib.error.HTTPError as e:
        print(f"Voice server error (HTTP {e.code}): {e.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"Could not reach voice server: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"TTS request failed: {e}", file=sys.stderr)
        return False
