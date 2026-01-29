# TDD RED Phase: Analysis

## Context

Analyze requirements and research findings to decompose the test
into concrete test cases with proper structure.

---

## Test Type Classification (REQUIRED)

Classify your test BEFORE writing it:

| Type | Marker | Scope | When to Use |
|------|--------|-------|-------------|
| **Unit** | `@pytest.mark.unit` | Single function/class | Testing isolated logic |
| **Integration** | `@pytest.mark.integration` | Multiple components | Testing component interaction |
| **E2E** | `@pytest.mark.e2e` | Full workflow | Testing user journeys |

**Decision Guide:**
- Does it mock external dependencies? → Unit
- Does it use real database/API? → Integration
- Does it simulate user actions end-to-end? → E2E

**Output:** Include `test_type: {unit|integration|e2e}` in analysis

---

## Focus Areas

1. **Test Case Decomposition**
   - Break down the requirement into specific assertions
   - Identify the AAA structure (Arrange-Act-Assert)
   - Plan the test data needed

2. **Edge Case Analysis**
   - Boundary conditions
   - Empty/null/undefined inputs
   - Error conditions

3. **Test Isolation**
   - What dependencies need mocking?
   - What shared state must be reset?
   - How to ensure test independence?

4. **Framework Alignment**
   - Map requirements to framework features
   - Identify needed imports/fixtures
   - Plan test organization

## Analysis Checklist

- [ ] Clear test name following conventions
- [ ] Arrange: All preconditions identified
- [ ] Act: Single action under test
- [ ] Assert: Specific, verifiable assertions
- [ ] Edge cases enumerated
- [ ] Mocking strategy defined

## Output Focus

Provide structured analysis:
- Test structure outline (AAA)
- Required imports/fixtures
- Mock/stub requirements
- Edge case test list
