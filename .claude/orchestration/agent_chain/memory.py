"""
Memory File Management

Handles reading and writing agent memory files for context passing.
"""

import re
from pathlib import Path
from typing import Dict, List

# Memory files location
MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"


class MemoryFile:
    """
    Manages agent memory file operations.

    Memory files follow a standard format:
    - Section 0: Context Loaded (task_id, flow_id, predecessors)
    - Section 1: Step Overview
    - Section 2: Johari Summary
    - Section 3: Downstream Directives
    """

    def __init__(self, task_id: str, agent_name: str):
        """
        Initialize MemoryFile.

        Args:
            task_id: Task identifier
            agent_name: Name of the agent
        """
        self.task_id = task_id
        self.agent_name = agent_name
        self._path = MEMORY_DIR / f"{task_id}-{agent_name}-memory.md"

    @property
    def path(self) -> Path:
        """Get the path to the memory file."""
        return self._path

    def exists(self) -> bool:
        """Check if the memory file exists."""
        return self._path.exists()

    def read(self) -> str:
        """
        Read the full content of the memory file.

        Returns:
            File content or empty string if not found
        """
        if not self.exists():
            return ""
        return self._path.read_text()

    def read_section(self, section_num: int) -> str:
        """
        Read a specific section from the memory file.

        Args:
            section_num: Section number (0-3)

        Returns:
            Section content or empty string if not found
        """
        content = self.read()
        if not content:
            return ""

        # Pattern to match section headers like "## Section 0: Context Loaded"
        pattern = rf"## Section {section_num}:.*?\n(.*?)(?=\n## Section \d+:|---|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def read_downstream_directives(self) -> str:
        """
        Read Section 3: Downstream Directives.

        This is what the next agent uses for context.

        Returns:
            Downstream directives content
        """
        return self.read_section(3)

    def write(self, content: str) -> None:
        """
        Write content to the memory file.

        Args:
            content: Full markdown content to write
        """
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._path.write_text(content)

    @classmethod
    def get_path(cls, task_id: str, agent_name: str) -> Path:
        """
        Get the expected path for a memory file.

        Args:
            task_id: Task identifier
            agent_name: Name of the agent

        Returns:
            Path to the memory file
        """
        return MEMORY_DIR / f"{task_id}-{agent_name}-memory.md"


def load_predecessor_context(
    task_id: str,
    predecessors: List[str],
) -> str:
    """
    Load context from predecessor agent memory files.

    Args:
        task_id: Task identifier
        predecessors: List of predecessor agent names

    Returns:
        Combined context from all predecessors
    """
    if not predecessors:
        return "No predecessor context available."

    context_parts = []

    for agent_name in predecessors:
        memory = MemoryFile(task_id, agent_name)

        if not memory.exists():
            context_parts.append(
                f"### {agent_name} (not available)\n"
                f"Memory file not found: {memory.path}"
            )
            continue

        directives = memory.read_downstream_directives()
        if directives:
            context_parts.append(f"### {agent_name}\n{directives}")
        else:
            # Fall back to full content if no directives section
            full_content = memory.read()
            # Truncate if too long
            if len(full_content) > 2000:
                full_content = full_content[:2000] + "\n... (truncated)"
            context_parts.append(f"### {agent_name}\n{full_content}")

    if not context_parts:
        return "No predecessor context loaded."

    return "\n\n".join(context_parts)


def get_all_memory_files(task_id: str) -> Dict[str, MemoryFile]:
    """
    Get all memory files for a task.

    Args:
        task_id: Task identifier

    Returns:
        Dict mapping agent names to MemoryFile instances
    """
    memory_files = {}
    pattern = f"{task_id}-*-memory.md"

    for path in MEMORY_DIR.glob(pattern):
        # Extract agent name from filename: {task_id}-{agent_name}-memory.md
        parts = path.stem.replace("-memory", "").split("-")
        if len(parts) >= 2:
            # Handle task_id that might contain dashes
            agent_name = parts[-1]
            memory_files[agent_name] = MemoryFile(task_id, agent_name)

    return memory_files


def verify_memory_file_exists(task_id: str, agent_name: str) -> bool:
    """
    Verify that a memory file exists.

    Args:
        task_id: Task identifier
        agent_name: Agent name

    Returns:
        True if memory file exists
    """
    return MemoryFile(task_id, agent_name).exists()
