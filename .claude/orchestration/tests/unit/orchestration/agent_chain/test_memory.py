"""
Unit tests for agent_chain/memory.py
"""

import pytest
from pathlib import Path

from orchestration.agent_chain.memory import (
    MemoryFile,
    load_predecessor_context,
    verify_memory_file_exists,
    MEMORY_DIR,
)


class TestMemoryFile:
    """Tests for MemoryFile class."""

    def test_path_construction(self):
        """MemoryFile should construct correct path."""
        memory = MemoryFile("task-123", "research")
        expected = MEMORY_DIR / "task-123-research-memory.md"
        assert memory.path == expected

    def test_get_path_classmethod(self):
        """get_path should return correct path."""
        path = MemoryFile.get_path("task-123", "research")
        expected = MEMORY_DIR / "task-123-research-memory.md"
        assert path == expected

    def test_exists_false(self):
        """exists should return False for non-existent file."""
        memory = MemoryFile("nonexistent-task", "research")
        assert memory.exists() is False

    def test_exists_true(self, tmp_path, monkeypatch):
        """exists should return True for existing file."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        # Create the memory file
        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text("# Test Memory")

        memory = MemoryFile("task-123", "research")
        assert memory.exists() is True

    def test_read_nonexistent(self):
        """read should return empty string for non-existent file."""
        memory = MemoryFile("nonexistent-task", "research")
        assert memory.read() == ""

    def test_read_existing(self, tmp_path, monkeypatch):
        """read should return file content."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        content = "# Research Memory\n\nTest content"
        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text(content)

        memory = MemoryFile("task-123", "research")
        assert memory.read() == content

    def test_write(self, tmp_path, monkeypatch):
        """write should create file with content."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        memory = MemoryFile("task-123", "research")
        memory.write("# Test Content")

        assert memory.exists()
        assert memory.read() == "# Test Content"

    def test_read_section(self, tmp_path, monkeypatch):
        """read_section should extract specific section."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        content = """# Research Memory

## Section 0: Context Loaded
Task ID: test-123

## Section 1: Step Overview
Did some research

## Section 2: Johari Summary
Known knowns here

## Section 3: Downstream Directives
Instructions for next agent

---
**RESEARCH_COMPLETE**
"""
        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text(content)

        memory = MemoryFile("task-123", "research")

        assert "Task ID: test-123" in memory.read_section(0)
        assert "Did some research" in memory.read_section(1)
        assert "Known knowns here" in memory.read_section(2)
        assert "Instructions for next agent" in memory.read_section(3)

    def test_read_section_not_found(self, tmp_path, monkeypatch):
        """read_section should return empty string if section not found."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        content = "# Memory\n\nNo sections here"
        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text(content)

        memory = MemoryFile("task-123", "research")
        assert memory.read_section(0) == ""

    def test_read_downstream_directives(self, tmp_path, monkeypatch):
        """read_downstream_directives should return Section 3."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        content = """# Memory

## Section 3: Downstream Directives
Do this next

---
"""
        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text(content)

        memory = MemoryFile("task-123", "research")
        assert "Do this next" in memory.read_downstream_directives()


class TestLoadPredecessorContext:
    """Tests for load_predecessor_context function."""

    def test_no_predecessors(self):
        """Should return message when no predecessors."""
        result = load_predecessor_context("task-123", [])
        assert "No predecessor context available" in result

    def test_missing_memory_file(self, tmp_path, monkeypatch):
        """Should indicate when memory file is missing."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        result = load_predecessor_context("task-123", ["clarification"])
        assert "clarification" in result
        assert "not available" in result.lower() or "not found" in result.lower()

    def test_loads_directives(self, tmp_path, monkeypatch):
        """Should load downstream directives from predecessor."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        content = """# Memory

## Section 3: Downstream Directives
Important instructions here
"""
        memory_path = tmp_path / "task-123-clarification-memory.md"
        memory_path.write_text(content)

        result = load_predecessor_context("task-123", ["clarification"])
        assert "clarification" in result
        assert "Important instructions here" in result

    def test_multiple_predecessors(self, tmp_path, monkeypatch):
        """Should load context from multiple predecessors."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        # Create memory files for two agents
        clarification_content = """# Memory
## Section 3: Downstream Directives
Clarification output
"""
        research_content = """# Memory
## Section 3: Downstream Directives
Research output
"""
        (tmp_path / "task-123-clarification-memory.md").write_text(
            clarification_content
        )
        (tmp_path / "task-123-research-memory.md").write_text(research_content)

        result = load_predecessor_context(
            "task-123",
            ["clarification", "research"],
        )
        assert "Clarification output" in result
        assert "Research output" in result


class TestVerifyMemoryFileExists:
    """Tests for verify_memory_file_exists function."""

    def test_returns_false_for_missing(self, tmp_path, monkeypatch):
        """Should return False for missing file."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        assert verify_memory_file_exists("task-123", "research") is False

    def test_returns_true_for_existing(self, tmp_path, monkeypatch):
        """Should return True for existing file."""
        monkeypatch.setattr(
            "orchestration.agent_chain.memory.MEMORY_DIR",
            tmp_path,
        )

        memory_path = tmp_path / "task-123-research-memory.md"
        memory_path.write_text("# Content")

        assert verify_memory_file_exists("task-123", "research") is True
