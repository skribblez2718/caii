---
name: orchestrate-clarification
description: Atomic skill for clarification using clarification agent
tags: atomic-skill, clarification, requirements
type: atomic
---

# orchestrate-clarification

**Type:** Atomic Skill
**Purpose:** Transform vague inputs into actionable specifications through systematic questioning

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| memory_file | string | Path to clarification output (`.claude/memory/task-{id}-clarification-memory.md`) |

## Exit Criteria

- [ ] Ambiguities resolved or explicitly documented as unknowns
- [ ] Requirements transformed to explicit specifications
- [ ] Success criteria defined and measurable
- [ ] Memory file written in standard format

## References

- `${CAII_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${CAII_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${CAII_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${CAII_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
