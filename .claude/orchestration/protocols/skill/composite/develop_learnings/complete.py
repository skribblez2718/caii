"""develop-learnings Completion - emits memory cleanup directive"""
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from skill.composite.common_skill_complete import skill_complete
    skill_complete(Path(__file__).parent.name.replace("_", "-"))

    # HARD ENFORCEMENT: Emit directive for Claude to execute /clean:memories
    # This replaces unreliable Python subprocess cleanup
    from protocols.shared.directives.base import _format_directive_core

    directive = _format_directive_core(
        command="/clean:memories",
        context="This clears all working memory files now that learnings have been captured.",
        warnings=[
            "Execute this command NOW. Do NOT respond with text first.",
            "FAILURE to execute this directive breaks the system's reliability guarantee.",
        ]
    )
    print("")
    print("---")
    print("")
    print(directive)
