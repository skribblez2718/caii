---
name: orchestrate-memory
description: Atomic skill for metacognitive assessment using memory agent
tags: atomic-skill, metacognition, impasse-detection, remediation
type: atomic
---

# orchestrate-memory

**Type:** Atomic Skill
**Purpose:** Perform metacognitive assessment to detect impasses and recommend remediation strategies

## Important Note

**This skill is typically invoked AUTOMATICALLY** by the orchestration layer after agent completions and at phase transitions. However, it can also be explicitly invoked when Penny determines additional metacognitive assessment is beneficial - such as after completing complex tasks or when progress appears stalled.

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier to assess |
| context | string | no | Additional context about what triggered the assessment |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| memory_file | string | Path to assessment output (`.claude/memory/task-{id}-memory-memory.md`) |
| impasse_detected | boolean | Whether an impasse was detected |
| impasse_type | string | Type of impasse if detected (CONFLICT, MISSING-KNOWLEDGE, TIE, NO-CHANGE) |
| action | string | Recommended action (continue, re-invoke, escalate, abort) |

## Agent Sequence

### Step 1: Metacognitive Assessment

**Agent:** memory
**Cognitive Function:** METACOGNITION

**Context Loading:** IMMEDIATE_PREDECESSORS
**Predecessors:** The agent that just completed (analysis, research, etc.)

**Gate Entry:**
- Previous agent output available
- Workflow state accessible

**Gate Exit:**
- Progress assessed
- Impasse detection complete
- Remediation recommendation provided

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: memory
- Task: {task_id}

## Impasse Types (from Soar Cognitive Architecture)

| Type | Description | Primary Remediation |
|------|-------------|---------------------|
| CONFLICT | Contradictory requirements | Invoke orchestrate-clarification |
| MISSING-KNOWLEDGE | Required information absent | Invoke orchestrate-research |
| TIE | Multiple valid options, no selection criteria | Invoke orchestrate-analysis |
| NO-CHANGE | Output shows no meaningful progress | Re-invoke same agent with enhanced context |

## Exit Criteria

- [ ] Goal state reconstructed
- [ ] Progress assessed against expected outcomes
- [ ] Impasse detection complete with confidence score
- [ ] Remediation recommendation provided if impasse detected
- [ ] Memory file written in standard format

## Token Constraints

**Maximum Output:** 800 tokens (STRICT)

The memory agent is designed for concise, actionable output. Prioritize essential information over verbose explanations.

## When This Skill is Auto-Invoked

1. **After Agent Completion:** When any cognitive agent finishes, the orchestration layer invokes metacognitive assessment
2. **At Phase Transitions:** When advancing from one workflow phase to another
3. **On Stall Detection:** When progress indicators suggest workflow stagnation

## Manual Invocation

Penny can explicitly invoke when metacognitive assessment would be beneficial:

```
/orchestrate-memory --task-id {task-id}
```

**Use cases for explicit invocation:**
- After completing a complex multi-step task
- When uncertain about progress or next steps
- To assess what should be retained in working memory
- When deciding between alternative approaches

## References

- `${PAI_DIRECTORY}/.claude/agents/memory.md` - Full agent definition
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/agent/memory/` - Protocol implementation
- `${PAI_DIRECTORY}/.claude/docs/cognitive-enhancements.md` - GoalMemory integration documentation
