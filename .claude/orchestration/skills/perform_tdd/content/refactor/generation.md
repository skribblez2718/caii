# TDD REFACTOR Phase: Generation

## Context

Generate refactored code based on the analysis. Apply improvements
while maintaining all existing behavior (tests must pass).

## Refactoring Guidelines

### Safe Refactoring Techniques

1. **Rename** - Variable, function, class names
2. **Extract** - Pull code into new functions/methods
3. **Inline** - Remove unnecessary indirection
4. **Move** - Relocate code to better locations

### Step-by-Step Approach

For each change:
1. Make ONE small change
2. Run tests
3. If pass, continue
4. If fail, revert and try differently

### Code Quality Goals

- Clear, self-documenting code
- DRY (Don't Repeat Yourself)
- SOLID principles where applicable
- Consistent style with codebase

## MANDATORY Code Standards

Same requirements as GREEN phase:

### 1. Absolute Imports Only

```python
# CORRECT
from orchestration.state.base import BaseState

# WRONG - FORBIDDEN
from .state.base import BaseState
```

### 2. Type Hints Required

All functions/methods MUST have complete type hints.

### 3. Docstrings Required (Google Style)

All public functions/classes MUST have docstrings with Args, Returns, Raises sections.

**Refactoring should IMPROVE compliance with these standards.**

## Output Requirements

Generate refactored code:
- All changes from analysis
- Maintain test compatibility
- Improve readability
- Follow existing patterns

## Verification Gate

After EACH refactoring step:
```bash
pytest {test_file} -v --tb=short
```

**All tests MUST pass before proceeding.**
