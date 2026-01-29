# TDD RED Phase: Clarification

## Context

You are clarifying requirements for writing a **failing test** in TDD.
The test must FAIL initially because no implementation exists yet.

## Focus Areas

1. **Behavior Specification**
   - What specific behavior should the test verify?
   - What are the expected inputs and outputs?
   - What edge cases need to be considered?

2. **Test Naming**
   - What naming convention to follow?
   - Pattern: `test_<what>_<scenario>_<expected_outcome>`

3. **Test Scope**
   - Is this a unit test, integration test, or e2e test?
   - What should be mocked vs tested for real?

4. **Acceptance Criteria**
   - What defines a "passing" test once implementation exists?
   - Are there specific assertions required?

## Constraints

- Test must be written BEFORE implementation
- Test must FAIL initially (no implementation exists)
- Test should verify ONE specific behavior

## Output Focus

Provide clear specification including:
- Test name (following naming convention)
- Expected inputs
- Expected outputs
- Edge cases to handle
- Any mocking requirements
