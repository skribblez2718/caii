"""Centralized directive formatting core.

This module provides the canonical formatting for MANDATORY directives
used across all orchestration protocols. By centralizing this logic,
we ensure consistent enforcement language and reduce code duplication.
"""
from typing import List, Optional

# Canonical header used across all directives
CANONICAL_HEADER = "**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**"


def _format_directive_core(
    command: str,
    context: str = "",
    warnings: Optional[List[str]] = None,
) -> str:
    """
    Core directive formatting with mandatory enforcement language.

    All protocol-specific formatters delegate to this function to ensure
    consistent enforcement patterns across the orchestration system.

    Args:
        command: The command to execute (without backticks)
        context: Additional context about what this accomplishes
        warnings: List of warning messages (each prefixed with warning emoji)

    Returns:
        Formatted directive string with mandatory enforcement language
    """
    if warnings is None:
        warnings = [
            "Execute this command NOW. Do NOT respond with text first.",
            "FAILURE to execute this directive breaks the system's reliability guarantee.",
        ]

    warning_text = "\n".join(f"\u26a0\ufe0f {w}" for w in warnings)

    directive = f"""
{CANONICAL_HEADER}
`{command}`

{warning_text}
{context}"""
    return directive.strip()
