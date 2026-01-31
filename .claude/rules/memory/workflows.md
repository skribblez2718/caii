---
paths:
  - ".claude/memory/**"
---

# Memory File Workflows

## Memory File Purpose

Memory files enable agent-to-agent context passing in workflows. Each agent writes findings that subsequent agents read.

## File Naming Convention

```
.claude/memory/{task_id}-{agent_name}-memory.md
```

Examples:
- `abc123-research-memory.md`
- `abc123-analysis-memory.md`
- `abc123-synthesis-memory.md`

## Standard Memory File Structure

```markdown
# Agent Output: {agent_name}

## Section 0: Context Loaded
```json
{
  "workflow_metadata_loaded": true,
  "workflow_file_path": ".claude/memory/task-{id}-memory.md",
  "predecessors_loaded": [...],
  "verification_status": "PASSED"
}
```

## Section 1: Step Overview
**Task ID:** {task-id}
**Step:** {step-number}
**Agent:** {agent_name}

{Narrative of work performed}

## Section 2: Johari Summary
```json
{
  "open": "Confirmed findings",
  "hidden": "Non-obvious discoveries",
  "blind": "Known limitations",
  "unknown": "Areas for investigation"
}
```

## Section 3: Downstream Directives
**Next Agent:** {agent-name}
**Handoff Context:** {Critical information for next agent}

## Section 4: User Questions (Optional)
{When clarification needed from user}
```

## Context Loading Patterns

| Pattern | Description |
|---------|-------------|
| **IMMEDIATE_PREDECESSORS** | Load only direct predecessor memory files |
| **ALL_PREDECESSORS** | Load all previous memory files in chain |
| **WORKFLOW_METADATA** | Load task-level metadata only |

## Token Management

Memory files must stay within token budgets:
- Keep sections concise
- Use compression techniques (lists over prose)
- Reference previous findings, don't repeat

## Memory File Lifecycle

1. **Create:** Agent writes memory file at end of execution
2. **Read:** Successor agents load predecessor memory
3. **Archive:** After workflow completion, files may be archived
4. **Clean:** Use `/clean:memories` to remove stale files

## Cleanup Commands

| Command | Effect |
|---------|--------|
| `/clean:memories` | Remove all memory files |
| `/clean:all` | Remove all state, plans, research, and memory |

## Agent Chain Context

Memory files are managed by the agent chain system:
- `agent_chain/memory.py` - MemoryFile class, load functions
- `agent_chain/state.py` - ChainState tracking
- `agent_chain/orchestrator.py` - Flow execution

## Writing Memory Files

Agents MUST use the Write tool to create memory files:

```python
# Memory file is MANDATORY - orchestration breaks without it
Write(".claude/memory/{task_id}-{agent}-memory.md", content)
```

**DO NOT:**
- Skip memory file creation
- Use non-standard paths
- Exceed token budgets
