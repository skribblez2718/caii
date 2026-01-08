---
name: orchestrate-generation
description: Atomic skill for generation using generation
tags: atomic-skill, generation, code, tdd
type: atomic
---

# orchestrate-generation

**Type:** Atomic Skill
**Purpose:** Generate code artifacts and deliverables using Test-Driven Development methodology

## Interface

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | string | yes | Workflow task identifier (format: `task-[a-z0-9-]{1,36}`) |
| implementation_scope | string | yes | What to implement (from synthesis/design output) |
| iteration | integer | no | Current TDD iteration (default: 1) |

### Output

| Output | Type | Description |
|--------|------|-------------|
| status | PASS\|FAIL | Execution result |
| tests_passing | boolean | Whether all tests pass |
| memory_file | string | Path to generation output (`.claude/memory/task-{id}-generation-memory.md`) |

## Agent Sequence

### Step 1: Generation

**Agent:** generation
**Cognitive Function:** GENERATION

**Context Loading:** IMMEDIATE_PREDECESSORS
**Predecessors:** synthesis (design/architecture)

**Gate Entry:**
- Design/architecture complete
- Implementation scope defined
- Test requirements understood

**Gate Exit:**
- Tests written first (RED)
- Implementation passes tests (GREEN)
- Code refactored for quality (REFACTOR)

**Memory Output:** Standard format per `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/`
- Agent: generation
- Task: {task_id}

**Protocol Extension:** `${PAI_DIRECTORY}/.claude/orchestration/shared-content/code-generation/` (required for code generation)

## TDD Cycle Requirements

### RED Phase
- Write failing tests first
- Tests define expected behavior
- Tests are specific and isolated

### GREEN Phase
- Write minimal code to pass tests
- No optimization during this phase
- Focus on correctness only

### REFACTOR Phase
- Improve code structure
- Maintain test passage
- Apply domain-specific patterns

## Code Generation Standards

Generation-agent MUST apply:

1. **Domain Patterns:** From task_domain (technical -> SOLID, security patterns)
2. **Quality Standards:** From workflow quality_standards
3. **TDD Discipline:** Strict RED-GREEN-REFACTOR cycle
4. **Security First:** OWASP compliance for web, input validation

## Iteration Support

For complex implementations requiring multiple TDD cycles:

```
iteration: 1  -> Core functionality
iteration: 2  -> Edge cases
iteration: 3  -> Error handling
iteration: N  -> Polish/optimization
```

Each iteration follows full RED-GREEN-REFACTOR cycle.

## Exit Criteria

- [ ] Tests written before implementation
- [ ] All tests passing
- [ ] Code refactored for maintainability
- [ ] Memory file written in standard format
- [ ] Artifacts documented in downstream_directives

## References

- `${PAI_DIRECTORY}/.claude/orchestration/shared-content/protocols/agent/` - Memory output format
- `${PAI_DIRECTORY}/.claude/docs/code-generation-reference.md` - Code generation requirements
- `${PAI_DIRECTORY}/.claude/docs/context-loading-reference.md` - Context loading patterns
- `${PAI_DIRECTORY}/.claude/docs/agent-protocol-reference.md` - Quick reference checklist
- `${PAI_DIRECTORY}/.claude/skills/develop-skill/resources/agent-invocation-template.md` - Invocation patterns
