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

## Agent Sequence

### Step 1: Research

**Agent:** research
**Cognitive Function:** RESEARCH

**Context Loading:** IMMEDIATE_PREDECESSORS
**Predecessors:** clarification (or workflow-metadata if first)

**Gate Entry:**
- Research scope defined
- Information gaps identified

**Gate Exit:**
- Sources evaluated
- Options compared
- Findings documented

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: research
- Task: {task_id}

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

- `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${PAI_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${PAI_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${PAI_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
