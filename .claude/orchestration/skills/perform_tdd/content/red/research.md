# TDD RED Phase: Research

## Context

Research existing test patterns in the codebase to write a failing test
that follows established conventions.

## Focus Areas

1. **Test File Structure**
   - Where are tests located? (`tests/`, `__tests__/`, `spec/`)
   - Naming conventions for test files
   - Directory organization (unit, integration, e2e)

2. **Testing Framework**
   - What framework is used? (pytest, jest, mocha, etc.)
   - Framework-specific patterns and idioms
   - Available assertions and matchers

3. **Existing Test Patterns**
   - How are fixtures/setup handled?
   - Mock/stub patterns in use
   - Common test utilities

4. **Related Tests**
   - Find similar tests for reference
   - Identify shared test utilities

## Tools to Use

- **Glob:** Find existing test files (`**/test_*.py`, `**/*.test.ts`)
- **Grep:** Search for test patterns, fixtures, mocks
- **Read:** Examine test examples for style reference

## Output Focus

Document in memory file:
- Test file location to use
- Framework and conventions
- Relevant fixture/mock patterns
- Example tests for reference
