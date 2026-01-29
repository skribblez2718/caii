# TDD GREEN Phase: Generation

## Context

Generate the MINIMAL implementation code to make the failing test pass.
Follow the analysis strictly - implement only what is required.

## Generation Guidelines

### Minimal Implementation

1. **Just Enough Code**
   - Make test pass with simplest solution
   - Hardcoded values are OK if that's all the test needs
   - Real logic only when test demands it

2. **Follow Existing Patterns**
   - Match codebase style
   - Use existing utilities
   - Consistent naming

3. **No Speculation**
   - Don't add "obvious" features not tested
   - Don't handle errors not tested
   - Don't optimize prematurely

### Code Quality (Still Matters)

- Correct syntax
- Proper imports
- Clear variable names
- No obvious bugs

## MANDATORY Code Standards

All generated code MUST follow these requirements:

### 1. Absolute Imports Only

```python
# CORRECT
from orchestration.state.base import BaseState
from package.module import function

# WRONG - FORBIDDEN
from .state.base import BaseState
from ..module import function
```

### 2. Type Hints Required

Every function/method MUST have complete type hints:

```python
def process(items: list[str], count: int) -> dict[str, int]:
    ...
```

Use modern syntax: `list[str]` not `List[str]`, `dict[str, int]` not `Dict[str, int]`.

### 3. PEP-Compliant Docstrings (Google Style)

Every function/class MUST have a docstring with:
- Summary line
- Args section (if parameters)
- Returns section (if non-None return)
- Raises section (if exceptions possible)

```python
def calculate_total(items: list[Item], discount: float = 0.0) -> float:
    """Calculate the total price of items with optional discount.

    Args:
        items: List of items to sum.
        discount: Discount percentage (0.0-1.0). Defaults to 0.0.

    Returns:
        Total price after discount applied.

    Raises:
        ValueError: If discount is not between 0.0 and 1.0.
    """
```

## Output Requirements

Generate implementation code:
- All necessary imports
- Function/class definitions
- Core logic to pass test
- No extra features

## Verification Gate

After implementation, ALL tests MUST pass:
```bash
pytest {test_file} -v --tb=short
```

If tests fail, iterate until GREEN.
