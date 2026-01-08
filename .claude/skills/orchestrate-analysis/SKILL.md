---
name: orchestrate-analysis
description: Atomic skill for analysis using analysis
tags: atomic-skill, analysis, complexity, risk
type: atomic
---

# orchestrate-analysis

**Type:** Atomic Skill
**Purpose:** Decompose complex problems, assess complexity, and identify risks and dependencies

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| memory_file | string | Path to analysis output (`.claude/memory/task-{id}-analysis-memory.md`) |

## Agent Sequence

### Step 1: Analysis

**Agent:** analysis
**Cognitive Function:** ANALYSIS

**Context Loading:** IMMEDIATE_PREDECESSORS
**Predecessors:** clarification (or workflow-metadata if first)

**Gate Entry:**
- Analysis scope defined
- Input artifacts available

**Gate Exit:**
- Complexity assessed
- Risks identified
- Dependencies mapped
- Patterns recognized

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: analysis
- Task: {task_id}

## Exit Criteria

- [ ] Problem decomposed into components
- [ ] Complexity scored and justified
- [ ] Risks identified with severity
- [ ] Dependencies mapped
- [ ] Memory file written in standard format

## References

- `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${PAI_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${PAI_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${PAI_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
