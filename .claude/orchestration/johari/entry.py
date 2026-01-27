"""
Johari Protocol Entry Point

Standalone protocol callable by agents to surface ambiguities.
"""

import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).parent


def load_protocol_content() -> str:
    """Load Johari protocol content."""
    protocol_file = CONTENT_DIR / "protocol.md"
    if protocol_file.exists():
        return protocol_file.read_text()
    return ""


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 entry.py '<context>'", file=sys.stderr)
        sys.exit(1)

    context = sys.argv[1]

    print("\n# JOHARI WINDOW DISCOVERY")
    print(f"\n**Context:** {context[:300]}...")

    # Load and print protocol content
    protocol_content = load_protocol_content()
    if protocol_content:
        print("\n---\n")
        print(protocol_content)

    # Print execution instructions
    print("\n---\n")
    print("## Execute Now\n")
    print("1. **SHARE:** Technical implications, risks, alternatives")
    print("2. **PROBE:** User intent, constraints, success criteria")
    print("3. **MAP:** Edge cases, assumptions, failure modes")
    print("4. **DELIVER:** If ANY ambiguity:")
    print("   - INVOKE AskUserQuestion tool")
    print("   - WAIT for response")


if __name__ == "__main__":
    main()
