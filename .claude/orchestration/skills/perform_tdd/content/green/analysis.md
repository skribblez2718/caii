# TDD GREEN Phase: Analysis

## Context

Analyze the failing test to determine the MINIMAL implementation
needed to make it pass. No more, no less.

## Focus Areas

1. **Test Understanding**
   - What assertion is failing?
   - What is the expected vs actual behavior?
   - What is the minimum needed to pass?

2. **Implementation Analysis**
   - What function/method needs to exist?
   - What parameters does it take?
   - What return value is expected?

3. **Dependency Analysis**
   - What imports are needed?
   - What existing code can be reused?
   - What minimal scaffolding is required?

4. **YAGNI Principle**
   - Only implement what the test requires
   - No extra features
   - No "future-proofing"

## Analysis Checklist

- [ ] Understood exact test failure
- [ ] Identified minimum code needed
- [ ] No unnecessary abstractions
- [ ] Clear implementation path

## Output Focus

Provide implementation plan:
- What file(s) to create/modify
- Function signature(s) needed
- Core logic outline
- Explicit: what NOT to implement yet
