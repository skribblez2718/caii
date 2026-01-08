---
name: orchestrate-validation
description: Atomic skill for quality validation using validation agent
tags: atomic-skill, validation, quality
type: atomic
---

# orchestrate-validation

**Type:** Atomic Skill
**Purpose:** Systematically verify artifacts and deliverables against established criteria

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |
| validation_target | string | yes | Agent whose output to validate (e.g., "generation") |
| quality_criteria | list | no | Additional quality criteria beyond workflow standards |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| verdict | GO\|NO-GO\|CONDITIONAL | Validation verdict |
| memory_file | string | Path to validation output (`.claude/memory/task-{id}-validation-memory.md`) |

## Agent Sequence

### Step 1: Validation

**Agent:** validation
**Cognitive Function:** VALIDATION

**Context Loading:** MULTIPLE_PREDECESSORS
**Predecessors:** {validation_target}, workflow-metadata

**Gate Entry:**
- Target artifact exists
- Quality criteria defined

**Gate Exit:**
- All criteria evaluated
- Issues documented with severity
- GO/NO-GO verdict issued

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: validation
- Task: {task_id}

## Validation Scope

Quality-validator evaluates against:

1. **Workflow Standards:** From task-{id}-memory.md quality_standards
2. **Domain Standards:** Based on task_domain classification
3. **Custom Criteria:** From quality_criteria parameter if provided

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| GO | All criteria pass | Proceed to next phase |
| NO-GO | Critical issues found | Return to generation for fixes |
| CONDITIONAL | Minor issues found | Proceed with documented caveats |

## Exit Criteria

- [ ] All quality criteria evaluated
- [ ] Issues categorized by severity (critical/major/minor)
- [ ] Verdict issued with justification
- [ ] Memory file written in standard format

## References

- `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${PAI_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${PAI_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${PAI_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
