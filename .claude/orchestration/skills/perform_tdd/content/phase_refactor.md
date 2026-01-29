# TDD REFACTOR Phase - Improve Code Quality

**Session:** {session_id} | **Cycle:** {cycle_count} | **Target:** {target_file} | **Test:** {test_file}

---

## CRITICAL: Virtual Environment

**BEFORE running any test or Python commands:**

1. **Locate venv:** Usually in project root (`.venv/`), but may be elsewhere:
   - Check `.claude/orchestration/.venv/` for CAII-style projects
   - Scan for `.venv/` or `venv/` directories if not in root

2. **Activate:** `source /path/to/.venv/bin/activate`

3. **Verify dependencies:** If `pytest` or other tools fail, install them:
   ```bash
   pip install pytest black pylint mypy pytest-cov
   ```

**NEVER run tests without activated virtual environment.**

---

## Objective

Improve code quality while keeping tests passing.

## Gate Requirement

**Tests MUST still pass** AND **quality MUST improve** before advancing to DOC.

## Agent Orchestration

1. **analysis**: Identify code smells, improvement opportunities, complexity metrics
2. **synthesis**: Create prioritized refactoring plan with atomic steps
3. **generation + validation** (iterative loop):
   - Apply ONE refactoring
   - Run tests
   - Verify pass
   - Repeat

## Refactoring Checklist

### Code Quality

- [ ] Run `make format` (black)
- [ ] Run `make lint` (pylint) - target 10/10
- [ ] Run type checker if applicable

### Code Smells to Address

| Smell | Solution |
|-------|----------|
| Duplicate code | Extract function/method |
| Long function | Break into smaller functions |
| Magic numbers | Define constants |
| Deep nesting | Early returns, guard clauses |
| Poor naming | Rename for clarity |

### Refactoring Safety Rules

1. **One change at a time** - Single atomic refactoring
2. **Test after each change** - Verify tests still pass
3. **Don't add features** - Behavior stays the same
4. **Commit incrementally** - Small, reversible changes

---

## Verification

After each refactoring:

```bash
make format && make lint && pytest {test_file} -v
```

**Required:**
- Tests pass
- `make lint` scores 10/10
- `make format` produces no changes

---

## Advance to DOC

After refactoring complete and quality gates pass:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/skills/tdd/advance.py --tdd-state {session_id}
```
