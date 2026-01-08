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

## Agent Sequence

### Step 1: Synthesis

**Agent:** synthesis
**Cognitive Function:** SYNTHESIS

**Context Loading:** MULTIPLE_PREDECESSORS
**Predecessors:** research, analysis (or workflow-metadata if first)

**Gate Entry:**
- Findings available for integration
- Design scope defined

**Gate Exit:**
- Disparate findings integrated
- Contradictions resolved
- Coherent recommendations produced
- Unified deliverable defined

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: synthesis
- Task: {task_id}

## Exit Criteria

- [ ] Multiple inputs integrated into unified output
- [ ] Contradictions identified and resolved
- [ ] Coherent recommendations documented
- [ ] Design/architecture defined (if applicable)
- [ ] Memory file written in standard format

## References

- `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${PAI_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${PAI_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${PAI_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
