---
name: perform-tdd
description: "Execute Test-Driven Development cycle with enforced RED-GREEN-REFACTOR-DOC phases. Use for implementing features, fixing bugs, writing code, or refactoring. General-purpose for all coding tasks requiring quality assurance."
disable-model-invocation: false
allowed-tools: Bash(pytest:*, make:*, python3:*), Glob, Grep, Read, Edit, Write, Task
---

# perform-tdd Skill

Test-Driven Development workflow enforcing the RED-GREEN-REFACTOR-DOC cycle through sequential phase execution.

---

## When to Use

- Implementing new features
- Fixing bugs
- Writing production code
- Refactoring existing code
- Adding new tests to existing code

## When NOT to Use

- Pure research or exploration tasks
- Documentation-only changes
- Configuration changes without behavior impact
- Quick one-line fixes with existing test coverage

---

## MANDATORY EXECUTION

Execute immediately to start or resume a TDD session:

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/entry.py --algorithm-state {session_id}
```

### With File Targets

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/entry.py \
  --algorithm-state {session_id} \
  --target src/module.py \
  --test tests/test_module.py
```

### Resume Existing Session

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/entry.py \
  --algorithm-state {session_id} \
  --perform-tdd-state {tdd_session_id}
```

---

## TDD Phases

| Phase | Objective | Gate Requirement |
|-------|-----------|------------------|
| **RED** | Write failing test(s) | Test exists AND fails |
| **GREEN** | Write minimal implementation | All tests pass |
| **REFACTOR** | Improve code quality | Tests pass + quality improved |
| **DOC** | Update documentation | Docs updated + accurate |

---

## Phase Commands

### Advance to Next Phase

After completing current phase requirements:

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/advance.py --perform-tdd-state {session_id}
```

### Complete Session

After DOC phase, to mark TDD cycle complete:

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/complete.py --perform-tdd-state {session_id}
```

### Loop Back for Next Feature

After DOC phase, to start new RED-GREEN-REFACTOR-DOC cycle:

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/complete.py --perform-tdd-state {session_id} --loop-back
```

---

## Agent Orchestration Per Phase

### RED Phase

1. **clarification** (conditional): Resolve ambiguous requirements
2. **research**: Find existing test patterns in codebase
3. **analysis**: Decompose requirement into test cases
4. **generation**: Write failing test using AAA pattern

### GREEN Phase

1. **research** (quick): Find minimal implementation patterns
2. **synthesis**: Design minimal implementation approach
3. **generation**: Write ONLY enough code to pass
4. **memory** (if stuck): Impasse detection

### REFACTOR Phase

1. **analysis**: Identify code smells, improvement opportunities
2. **synthesis**: Create prioritized refactoring plan
3. **generation + validation** (loop): Apply refactoring, verify tests

### DOC Phase

1. **analysis**: Identify documentation gaps
2. **generation**: Update documentation
3. **validation**: Verify accuracy and completeness

---

## Quick Test Commands

After activating virtual environment (`source .venv/bin/activate`):

| Action | Command |
|--------|---------|
| Run tests | `make test` or `pytest` |
| Format code | `make format` |
| Lint code | `make lint` |
| Run specific test | `pytest tests/path/test_file.py -v` |

---

## Virtual Environment Requirement

**CRITICAL:** Always activate virtual environment before running tests:

```bash
cd ${CAII_DIRECTORY}/.claude/orchestration
source .venv/bin/activate
```

Tests will fail with `ModuleNotFoundError` without activated venv.

---

## Resources

- `.claude/skills/perform-tdd/resources/tdd-workflow.md` - TDD cycle reference
- `.claude/skills/perform-tdd/resources/test-patterns.md` - Testing patterns by language
- `.claude/skills/perform-tdd/resources/refactoring-catalog.md` - Refactoring techniques

---

## State Management

TDD sessions are tracked in:
- State files: `.claude/orchestration/skills/perform_tdd/state/perform-tdd-{session_id}.json`
- Linked to parent algorithm via `parent_algorithm_id`

Session state includes:
- Current phase
- Cycle count
- Target/test files
- Phase outputs
