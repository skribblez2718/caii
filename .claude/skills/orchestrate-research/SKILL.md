---
name: orchestrate-research
description: Atomic skill for research using research agent
tags: atomic-skill, research, discovery
type: atomic
---

# orchestrate-research

**Type:** Atomic Skill
**Purpose:** Investigate options, gather domain knowledge, and document findings

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |
| research_depth | string | no | quick\|standard\|deep (default: standard) |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| memory_file | string | Path to research output (`.claude/memory/task-{id}-research-memory.md`) |

## Research Depth Configuration

| Depth | Behavior | Use Case |
|-------|----------|----------|
| quick | Surface-level scan, key findings only | Time-sensitive decisions |
| standard | Balanced investigation, multiple sources | Most research tasks |
| deep | Comprehensive analysis, exhaustive sources | Critical decisions |

## Exit Criteria

- [ ] Research scope covered
- [ ] Sources evaluated and documented
- [ ] Findings documented with evidence
- [ ] Memory file written in standard format

## References

- `${CAII_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${CAII_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${CAII_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${CAII_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
