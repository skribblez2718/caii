"""
Orchestration Utilities

Shared utility functions for all orchestration scripts.
Keep orchestration code DRY and modular.
"""

from pathlib import Path


def get_content_dir(script_path: str) -> Path:
    """
    Get the content directory relative to a script.

    Convention: content/ directory is sibling to the script.

    Args:
        script_path: Pass __file__ from the calling script

    Returns:
        Path to content/ directory
    """
    return Path(script_path).parent / "content"


def load_content(script_path: str, filename: str) -> str:
    """
    Load markdown content from the content directory.

    Args:
        script_path: Pass __file__ from the calling script
        filename: Name of content file (with .md extension)

    Returns:
        Content string, or empty string if not found
    """
    content_dir = get_content_dir(script_path)
    content_file = content_dir / filename
    if content_file.exists():
        return content_file.read_text()
    return ""


def substitute_placeholders(content: str, **kwargs: str) -> str:
    """
    Substitute {placeholder} variables in content.

    Args:
        content: String with {placeholder} markers
        **kwargs: key=value pairs to substitute

    Returns:
        Content with placeholders replaced
    """
    result = content
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result
