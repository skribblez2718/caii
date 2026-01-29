# TDD RED Phase: Generation

## Context

Generate the failing test code based on clarification, research, and analysis.
The test MUST fail when run (no implementation exists yet).

## Generation Guidelines

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

### Test Quality Requirements

1. **Single Responsibility**
   - Test ONE specific behavior
   - Single reason to fail

2. **Self-Documenting**
   - Test name describes expected behavior
   - Comments only for non-obvious setup

3. **Independent**
   - No dependency on other tests
   - No shared mutable state

4. **Repeatable**
   - Same result every run
   - No time-dependent assertions

5. **Import Standards**
   - ABSOLUTE imports only (no relative imports)
   - Example: `from orchestration.module import X` NOT `from .module import X`

6. **Type Hints**
   - All function parameters and returns MUST have type hints
   - Use modern syntax: `list[str]` not `List[str]`

## REQUIRED: Test Marker

Every test MUST include the appropriate pytest marker:

```python
import pytest

@pytest.mark.unit  # or @pytest.mark.integration or @pytest.mark.e2e
def test_function_does_something():
    # AAA pattern
    pass
```

**Gate:** Test without marker will fail validation.

---

## Output Requirements

Generate complete test code:
- All necessary imports
- Test function(s) with descriptive names
- Clear AAA structure
- Assertions that will FAIL
- **Appropriate pytest marker** (unit/integration/e2e)

## Verification

After generating, the test MUST:
1. Run without syntax errors
2. FAIL with clear error message
3. Fail for the RIGHT reason (missing implementation)
