#!/usr/bin/env python3
"""
PostToolUse hook test - Does stdout reach Claude's context?

This is a temporary test hook to determine if PostToolUse stdout
can be used to inject content into Claude's context.

If this works, we can use PostToolUse for ExitPlanMode to trigger
the reasoning protocol immediately after plan approval.
"""
import sys
import json


def main():
    try:
        hook_data = json.load(sys.stdin)
        tool_name = hook_data.get("tool_name", "unknown")

        # Print a distinctive message (NO <system-reminder> tags)
        print(f"""
---
**TEST: PostToolUse stdout test for tool: {tool_name}**

If you (Claude/Penny) can see this message, PostToolUse stdout DOES reach your context.
Please acknowledge seeing this message by saying "I see the PostToolUse test message".
---
""")
        return 0
    except Exception as e:
        print(f"Test hook error: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
