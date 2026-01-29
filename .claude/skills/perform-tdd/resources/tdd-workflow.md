# TDD Workflow Reference

## The Cycle

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌─────┐    ┌───────┐    ┌──────────┐    ┌─────┐      │
│   │ RED │───>│ GREEN │───>│ REFACTOR │───>│ DOC │      │
│   └─────┘    └───────┘    └──────────┘    └──┬──┘      │
│      ^                                       │         │
│      │              loop-back                │         │
│      └───────────────────────────────────────┘         │
│                         OR                              │
│                    COMPLETED                            │
└─────────────────────────────────────────────────────────┘
```

---

## Phase Details

### RED: Write Failing Test

**Goal:** Define expected behavior through a failing test.

**Steps:**
1. Understand the requirement
2. Write test FIRST (before any implementation)
3. Run test - verify it fails
4. Commit failing test (optional)

**Gate:** Test exists AND fails for the right reason.

---

### GREEN: Make It Pass

**Goal:** Write minimal code to make the test pass.

**Steps:**
1. Write only enough code to pass
2. No optimization, no extras
3. Run test - verify it passes
4. Run all tests - ensure no regression

**Gate:** ALL tests pass.

---

### REFACTOR: Improve Quality

**Goal:** Clean up while keeping tests green.

**Steps:**
1. Identify code smells
2. Apply one refactoring at a time
3. Run tests after each change
4. Run formatter and linter

**Gate:** Tests pass + quality metrics met.

---

### DOC: Update Documentation

**Goal:** Keep documentation current.

**Steps:**
1. Update docstrings
2. Update README if needed
3. Update CLAUDE.md if architecture changed
4. Verify accuracy

**Gate:** Documentation accurate and complete.

---

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Test First** | Never write production code without a failing test |
| **Minimal Code** | Write only enough to pass the test |
| **Incremental** | Small steps, frequent feedback |
| **No Regression** | All tests must pass at all times |
| **Clean Code** | Refactor after green, not before |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem |
|--------------|---------|
| Writing test after code | Loses design benefits |
| Writing too much test | Tests become brittle |
| Skipping GREEN | Over-engineering |
| Skipping REFACTOR | Technical debt |
| Skipping DOC | Knowledge loss |

---

## Cycle Frequency

- **Single feature:** One cycle per feature
- **Bug fix:** One cycle per bug
- **Refactoring:** May skip RED if tests exist
- **Complex feature:** Multiple cycles, one per sub-feature
