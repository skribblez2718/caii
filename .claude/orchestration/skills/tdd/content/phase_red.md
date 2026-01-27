# TDD RED Phase - Write Failing Test

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

Write a failing test that defines the expected behavior.

## Gate Requirement

**Test MUST exist AND fail** before advancing to GREEN.

## Agent Orchestration

1. **clarification** (conditional): If requirement is ambiguous, resolve first
2. **research**: Find existing test patterns in codebase
3. **analysis**: Decompose requirement into test cases, identify edge cases
4. **generation**: Write failing test(s) using AAA pattern

## Test Writing Guidelines

### AAA Pattern (Arrange-Act-Assert)

```python
def test_descriptive_name():
    # Arrange - Set up preconditions
    input_data = setup_test_data()

    # Act - Perform the action
    result = function_under_test(input_data)

    # Assert - Verify outcome
    assert result == expected_value
```

### Naming Convention

```
test_<what>_<scenario>_<expected_outcome>

Examples:
- test_generate_session_id_returns_12_chars
- test_fsm_transition_from_red_to_green_succeeds
- test_state_load_with_missing_file_returns_none
```

### Test Categories

- **Happy path:** Normal expected behavior
- **Edge cases:** Boundary conditions, empty inputs
- **Error cases:** Invalid inputs, exceptions

---

## Verification

Run the test to confirm it fails:

```bash
pytest {test_file} -v --tb=short
```

**Expected:** Test should FAIL (because implementation doesn't exist yet).

---

## Advance to GREEN

After test fails for the right reason:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/skills/tdd/advance.py --tdd-state {session_id}
```
