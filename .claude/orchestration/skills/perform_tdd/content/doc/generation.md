# TDD DOC Phase: Generation

## Context

Generate documentation based on the analysis. Add docstrings,
update external docs, and ensure the code is self-documenting.

## Documentation Guidelines

### Docstring Format (Python - Google Style)

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief one-line description.

    Longer description if needed, explaining behavior,
    assumptions, and edge cases.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When X happens
        TypeError: When Y happens

    Example:
        >>> function_name("foo", 42)
        "result"
    """
```

### Class Docstrings

```python
class ClassName:
    """
    Brief one-line description.

    Longer description explaining the class purpose,
    usage patterns, and important behaviors.

    Attributes:
        attr1: Description
        attr2: Description

    Example:
        >>> obj = ClassName()
        >>> obj.method()
    """
```

### Quality Standards

1. **Be Accurate** - Doc matches actual behavior
2. **Be Concise** - No unnecessary words
3. **Be Helpful** - Answer "what does this do?"
4. **Examples** - When behavior isn't obvious

## Output Requirements

Generate documentation:
- Docstrings for all public functions/classes
- Type hints where missing
- Updated CLAUDE.md (if applicable)
- Updated README (if public API changed)

## TDD Cycle Complete

After DOC phase:
- Code is tested
- Code is clean
- Code is documented
- Ready for review/commit
