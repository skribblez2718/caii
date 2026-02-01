"""
Agent Invocation Directive Builder

Builds complete directives for invoking agents, including:
- Protocol content from skill phase
- Predecessor context from memory files
- Memory output requirements
"""

from pathlib import Path
from typing import List, Optional

from orchestration.agents.config import get_agent_config
from orchestration.agent_chain.memory import load_predecessor_context


def build_learnings_directive(agent_name: str) -> str:
    """
    Build a MANDATORY learnings directive for an agent.

    This instructs the agent to scan and read relevant learnings
    BEFORE performing any cognitive work.

    Args:
        agent_name: Name of the agent (maps to learnings directory)

    Returns:
        Formatted MANDATORY directive string
    """
    # Create uppercase prefix for learning IDs (e.g., "R" for research -> "R-H-001")
    prefix = agent_name[0].upper()

    return f"""# MANDATORY: Load Learnings First

**STOP. Before ANY other action, you MUST execute these steps:**

## Step 1: Scan Learnings INDEX

Read the INDEX sections from these files:
- `.claude/learnings/{agent_name}/heuristics.md`
- `.claude/learnings/{agent_name}/anti-patterns.md`
- `.claude/learnings/{agent_name}/checklists.md`

The INDEX section is between `## INDEX (Always Loaded)` and `---`.

## Step 2: Identify Relevant Learnings

Based on your task context, identify which learning IDs are relevant:
- Match learning descriptions to your task requirements
- Note IDs like `{prefix}-H-001`, `{prefix}-A-003`, etc.

## Step 3: Read Full Entries

For each relevant ID, read the full entry from the "## Full Entries Below" section.

## Step 4: Apply Learnings

Keep relevant learnings in mind as you proceed with your task.

**If files contain `<!-- No learnings yet -->`, proceed without them.**

---

**This step is NON-NEGOTIABLE.** Only after completing this may you proceed to your protocol instructions below.

---

"""


def load_content(content_file: str, skill_content_dir: Path) -> str:
    """
    Load protocol content from a skill's content directory.

    Args:
        content_file: Relative path within content dir (e.g., "red/clarification.md")
        skill_content_dir: Path to the skill's content directory

    Returns:
        Content string or placeholder if not found
    """
    content_path = skill_content_dir / content_file
    if content_path.exists():
        return content_path.read_text()
    return f"<!-- Protocol content not found: {content_file} -->"


def build_agent_invocation_directive(
    task_id: str,
    agent_name: str,
    flow_id: str,
    content_file: Optional[str] = None,
    predecessors: Optional[List[str]] = None,
    skill_content_dir: Optional[Path] = None,
    skill_name: Optional[str] = None,
    phase_id: Optional[str] = None,
    domain: str = "technical",
    task_description: str = "",
    include_learnings_directive: bool = False,
) -> str:
    """
    Build a complete directive for invoking an agent.

    The directive includes:
    1. Learnings Directive (if first invocation for this agent)
    2. Protocol Instructions (from content file)
    3. Predecessor Context (from memory files)
    4. Memory Output Requirements

    Args:
        task_id: Unique task identifier
        agent_name: Name of the agent to invoke
        flow_id: Identifier of the flow being executed
        content_file: Path to protocol content file (relative to skill content dir)
        predecessors: List of predecessor agent names to load context from
        skill_content_dir: Path to skill's content directory
        skill_name: Name of the skill (for context)
        phase_id: Phase ID within the skill (for context)
        domain: Task domain (technical, personal, creative, etc.)
        task_description: Brief description of the task
        include_learnings_directive: Whether to include MANDATORY learnings directive

    Returns:
        Complete formatted directive string
    """
    predecessors = predecessors or []
    agent_config = get_agent_config(agent_name) or {}
    cognitive_function = agent_config.get("cognitive_function", agent_name.upper())

    # Load task-specific protocol content
    protocol_content = ""
    if content_file and skill_content_dir:
        protocol_content = load_content(content_file, skill_content_dir)

    # Load predecessor context from memory files
    predecessor_context = load_predecessor_context(task_id, predecessors)

    # Build the directive
    directive_parts = []

    # LEARNINGS DIRECTIVE FIRST (if needed)
    if include_learnings_directive:
        directive_parts.append(build_learnings_directive(agent_name))

    directive_parts.extend(
        [
            f"## Agent Invocation: {agent_name}",
            "",
            f"**Task ID:** `{task_id}`",
            f"**Flow:** `{flow_id}`",
            f"**Agent:** `{agent_name}` ({cognitive_function})",
        ]
    )

    if skill_name:
        directive_parts.append(f"**Skill:** `{skill_name}`")
    if phase_id:
        directive_parts.append(f"**Phase:** `{phase_id}`")
    directive_parts.append(f"**Domain:** `{domain}`")

    if task_description:
        directive_parts.extend(["", f"**Task:** {task_description}"])

    # Protocol Instructions
    if protocol_content:
        directive_parts.extend(
            [
                "",
                "---",
                "",
                "### Protocol Instructions",
                "",
                protocol_content,
            ]
        )

    # Predecessor Context
    if predecessors:
        directive_parts.extend(
            [
                "",
                "---",
                "",
                "### Predecessor Context",
                "",
                predecessor_context,
            ]
        )

    # Memory Output Requirements
    memory_path = f".claude/memory/{task_id}-{agent_name}-memory.md"
    directive_parts.extend(
        [
            "",
            "---",
            "",
            "### Memory Output",
            "",
            f"Write to: `{memory_path}`",
            "",
            "**Required sections:**",
            "",
            "- Section 0: Context Loaded (task_id, flow_id, predecessors)",
            "- Section 1: Step Overview (what was done, key decisions)",
            "- Section 2: Johari Summary (Known Knowns, Known Unknowns, Unknown Unknowns)",
            "- Section 3: Downstream Directives (instructions for next agent)",
        ]
    )

    return "\n".join(directive_parts)


def build_task_tool_directive(
    task_id: str,
    agent_name: str,
    prompt: str,
    model: Optional[str] = None,
) -> str:
    """
    Build a directive instructing DA to use the Task tool.

    Args:
        task_id: Task identifier
        agent_name: Name of the agent (maps to subagent_type)
        prompt: The full prompt for the agent
        model: Optional model override (sonnet, opus, haiku)

    Returns:
        Directive text for DA to execute
    """
    model_str = model if model else "sonnet"
    short_id = task_id[:8]

    # Indent the prompt for YAML-like formatting
    indented_prompt = "\n".join(f"  {line}" for line in prompt.split("\n"))

    return f"""**MANDATORY - INVOKE TASK TOOL NOW**

⚠️  DO NOT perform this work yourself. DO NOT write code, tests, or documentation directly.

You MUST invoke the Task tool with these EXACT parameters:

<task_tool_invocation>
subagent_type: "{agent_name}"
description: "Execute {agent_name} for task {short_id}"
model: "{model_str}"
prompt: |
{indented_prompt}
</task_tool_invocation>

**STOP.** Invoke the Task tool now. Wait for the agent to complete before proceeding.
"""
