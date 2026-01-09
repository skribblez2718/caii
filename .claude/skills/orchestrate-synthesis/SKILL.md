---
name: orchestrate-synthesis
description: Atomic skill for synthesis using synthesis
tags: atomic-skill, synthesis, integration, design
type: atomic
---

# orchestrate-synthesis

**Type:** Atomic Skill
**Purpose:** Integrate disparate findings into coherent recommendations and produce unified deliverables

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| memory_file | string | Path to synthesis output (`.claude/memory/task-{id}-synthesis-memory.md`) |

## Exit Criteria

- [ ] Multiple inputs integrated into unified output
- [ ] Contradictions identified and resolved
- [ ] Coherent recommendations documented
- [ ] Design/architecture defined (if applicable)
- [ ] Memory file written in standard format

## References

- `${CAII_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${CAII_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${CAII_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${CAII_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
