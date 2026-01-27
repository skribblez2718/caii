# TDD GREEN Phase - Make Test Pass

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

Write the MINIMAL implementation to make the test pass.

## Gate Requirement

**ALL tests MUST pass** before advancing to REFACTOR.

## Agent Orchestration

1. **research** (quick): Find minimal implementation patterns
2. **synthesis**: Design minimal implementation approach
3. **generation**: Write ONLY enough code to pass
4. **memory** (if stuck): Impasse detection and remediation

## Implementation Guidelines

### Minimal Code Principle

Write ONLY the code needed to pass the test:

- No extra features
- No premature optimization
- No error handling beyond what tests require
- Simple and direct

### Common Anti-Patterns to AVOID

- Adding "nice to have" features
- Handling edge cases not covered by tests
- Optimizing before tests pass
- Adding logging/comments beyond necessity

---

## Verification

Run ALL tests to confirm they pass:

```bash
pytest {test_file} -v
```

**Expected:** All tests should PASS.

If tests fail, iterate on implementation until they pass.

---

## Advance to REFACTOR

After all tests pass:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/skills/tdd/advance.py --tdd-state {session_id}
```
