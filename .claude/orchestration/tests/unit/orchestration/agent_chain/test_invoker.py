"""
Unit tests for agent_chain/invoker.py
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestration.agent_chain.invoker import (
    build_learnings_directive,
    build_agent_invocation_directive,
    build_task_tool_directive,
    load_content,
)


class TestBuildLearningsDirective:
    """Tests for build_learnings_directive function."""

    def test_build_learnings_directive_format(self):
        """Directive should have MANDATORY header and steps."""
        directive = build_learnings_directive("research")

        assert "# MANDATORY: Load Learnings First" in directive
        assert "## Step 1: Scan Learnings INDEX" in directive
        assert "## Step 2: Identify Relevant Learnings" in directive
        assert "## Step 3: Read Full Entries" in directive
        assert "## Step 4: Apply Learnings" in directive
        assert "NON-NEGOTIABLE" in directive

    def test_build_learnings_directive_agent_name_substitution(self):
        """Directive should include correct agent name and paths."""
        directive = build_learnings_directive("clarification")

        assert ".claude/learnings/clarification/heuristics.md" in directive
        assert ".claude/learnings/clarification/anti-patterns.md" in directive
        assert ".claude/learnings/clarification/checklists.md" in directive

    def test_build_learnings_directive_prefix_generation(self):
        """Directive should use uppercase first letter for ID prefix."""
        directive = build_learnings_directive("research")
        assert "R-H-001" in directive
        assert "R-A-003" in directive

        directive = build_learnings_directive("analysis")
        assert "A-H-001" in directive
        assert "A-A-003" in directive

    def test_build_learnings_directive_handles_empty_learnings(self):
        """Directive should mention how to handle empty learnings files."""
        directive = build_learnings_directive("research")
        assert "<!-- No learnings yet -->" in directive
        assert "proceed without them" in directive


class TestBuildAgentInvocationDirective:
    """Tests for build_agent_invocation_directive function."""

    @patch("orchestration.agent_chain.invoker.get_agent_config")
    @patch("orchestration.agent_chain.invoker.load_predecessor_context")
    def test_without_learnings(self, mock_context, mock_config):
        """Directive without learnings should not include learnings section."""
        mock_config.return_value = {"cognitive_function": "RESEARCH"}
        mock_context.return_value = ""

        directive = build_agent_invocation_directive(
            task_id="test-123",
            agent_name="research",
            flow_id="test-flow",
            include_learnings_directive=False,
        )

        assert "# MANDATORY: Load Learnings First" not in directive
        assert "## Agent Invocation: research" in directive

    @patch("orchestration.agent_chain.invoker.get_agent_config")
    @patch("orchestration.agent_chain.invoker.load_predecessor_context")
    def test_with_learnings(self, mock_context, mock_config):
        """Directive with learnings should include learnings section at top."""
        mock_config.return_value = {"cognitive_function": "RESEARCH"}
        mock_context.return_value = ""

        directive = build_agent_invocation_directive(
            task_id="test-123",
            agent_name="research",
            flow_id="test-flow",
            include_learnings_directive=True,
        )

        assert "# MANDATORY: Load Learnings First" in directive
        assert "## Agent Invocation: research" in directive
        # Learnings should come BEFORE agent invocation
        learnings_pos = directive.find("# MANDATORY: Load Learnings First")
        invocation_pos = directive.find("## Agent Invocation: research")
        assert learnings_pos < invocation_pos

    @patch("orchestration.agent_chain.invoker.get_agent_config")
    @patch("orchestration.agent_chain.invoker.load_predecessor_context")
    def test_includes_task_context(self, mock_context, mock_config):
        """Directive should include task context fields."""
        mock_config.return_value = {"cognitive_function": "CLARIFICATION"}
        mock_context.return_value = ""

        directive = build_agent_invocation_directive(
            task_id="test-123",
            agent_name="clarification",
            flow_id="test-flow",
            skill_name="perform-tdd",
            phase_id="red",
            domain="technical",
            task_description="Write failing test",
        )

        assert "**Task ID:** `test-123`" in directive
        assert "**Flow:** `test-flow`" in directive
        assert "**Skill:** `perform-tdd`" in directive
        assert "**Phase:** `red`" in directive
        assert "**Domain:** `technical`" in directive
        assert "**Task:** Write failing test" in directive

    @patch("orchestration.agent_chain.invoker.get_agent_config")
    @patch("orchestration.agent_chain.invoker.load_predecessor_context")
    def test_includes_memory_output_requirements(self, mock_context, mock_config):
        """Directive should include memory file output requirements."""
        mock_config.return_value = {"cognitive_function": "RESEARCH"}
        mock_context.return_value = ""

        directive = build_agent_invocation_directive(
            task_id="test-123",
            agent_name="research",
            flow_id="test-flow",
        )

        assert "### Memory Output" in directive
        assert ".claude/memory/test-123-research-memory.md" in directive
        assert "Section 0: Context Loaded" in directive
        assert "Section 3: Downstream Directives" in directive


class TestLoadContent:
    """Tests for load_content function."""

    def test_load_existing_content(self, tmp_path):
        """Should load content from existing file."""
        content_file = tmp_path / "phase" / "agent.md"
        content_file.parent.mkdir(parents=True, exist_ok=True)
        content_file.write_text("Test content")

        result = load_content("phase/agent.md", tmp_path)

        assert result == "Test content"

    def test_load_missing_content(self, tmp_path):
        """Should return placeholder for missing file."""
        result = load_content("missing/file.md", tmp_path)

        assert "Protocol content not found" in result
        assert "missing/file.md" in result


class TestBuildTaskToolDirective:
    """Tests for build_task_tool_directive function."""

    def test_includes_mandatory_header(self):
        """Directive should include MANDATORY header."""
        directive = build_task_tool_directive(
            task_id="test-123456",
            agent_name="research",
            prompt="Test prompt",
        )

        assert "**MANDATORY - INVOKE TASK TOOL NOW**" in directive

    def test_includes_task_tool_invocation_block(self):
        """Directive should include task_tool_invocation block."""
        directive = build_task_tool_directive(
            task_id="test-123456",
            agent_name="research",
            prompt="Test prompt",
        )

        assert "<task_tool_invocation>" in directive
        assert 'subagent_type: "research"' in directive
        assert 'model: "sonnet"' in directive
        assert "Test prompt" in directive

    def test_uses_custom_model(self):
        """Directive should use custom model if provided."""
        directive = build_task_tool_directive(
            task_id="test-123456",
            agent_name="research",
            prompt="Test prompt",
            model="opus",
        )

        assert 'model: "opus"' in directive

    def test_truncates_task_id_in_description(self):
        """Description should use first 8 chars of task_id."""
        directive = build_task_tool_directive(
            task_id="abcd1234efgh5678",
            agent_name="research",
            prompt="Test prompt",
        )

        assert "task abcd1234" in directive
        assert "abcd1234efgh5678" not in directive.split("prompt:")[0]
