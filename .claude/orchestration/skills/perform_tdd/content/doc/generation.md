# TDD DOC Phase: Generation

## Context

Generate documentation based on the analysis. This phase produces
production-grade documentation including README, CLAUDE.md files,
OpenAPI specs, and code docstrings.

---

## README Template (Production-Grade)

When creating or updating README, use this structure:

```markdown
# Project Name

Brief one-line description of what this project does.

## Description

Expanded description covering:
- What problem this solves
- Key features and capabilities
- Target audience/use cases

## Installation

### Prerequisites

- List required software (Python version, Node.js, etc.)
- System dependencies

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd <project-name>

# Install dependencies
<package-manager> install

# Configure environment (if needed)
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Basic Usage

```bash
# Example command or code snippet
<command-or-code>
```

### Common Workflows

Describe 2-3 common use cases with examples.

## Testing

```bash
# Run all tests
<test-command>

# Run specific test suite
<test-command-specific>

# Check coverage
<coverage-command>
```

## API Reference

[Link to OpenAPI spec or API documentation]

Or inline documentation for small APIs.

## Contributing

### Development Setup

```bash
# Additional dev dependencies
<dev-install-command>

# Run linter
<lint-command>

# Run formatter
<format-command>
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit PR with description

## License

[License type] - See [LICENSE](LICENSE) for details.
```

---

## CLAUDE.md Template

### Project Root CLAUDE.md

```markdown
# Project Name

Brief description and purpose.

## Architecture Overview

```
project/
├── src/           # Main source code
├── tests/         # Test suite
├── docs/          # Documentation
└── config/        # Configuration files
```

## Key Concepts

- **Concept 1:** Brief explanation
- **Concept 2:** Brief explanation

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Run tests | `<command>` |
| Build | `<command>` |
| Main entry | `src/main.py` |

## Development Patterns

- Pattern 1 used and why
- Pattern 2 used and why

## Important Files

| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point |
| `config/settings.py` | Configuration management |

---

*Last updated: YYYY-MM-DD*
```

### Subdirectory CLAUDE.md

```markdown
# Directory Name

## Purpose

What this directory contains and why it exists.

## Key Files

| File | Purpose |
|------|---------|
| `file1.py` | Brief description |
| `file2.py` | Brief description |

## Patterns Used

- Describe any patterns specific to this directory
- Note any conventions followed here

## Dependencies

- Internal: What other project directories this depends on
- External: Key external packages used

## Usage

How other parts of the codebase use this directory's exports.

---

*Last updated: YYYY-MM-DD*
```

---

## OpenAPI Spec Template (3.0+)

When API endpoints exist, generate or update OpenAPI spec:

**Standard Location:** `docs/openapi.yaml` or `openapi.yaml` at project root

```yaml
openapi: 3.0.3
info:
  title: API Name
  description: Brief API description
  version: 1.0.0

servers:
  - url: http://localhost:8000
    description: Development server

paths:
  /endpoint:
    get:
      summary: Brief description
      description: Detailed description
      operationId: operationName
      parameters:
        - name: param1
          in: query
          description: Parameter description
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseModel'
        '400':
          description: Bad request
        '404':
          description: Not found

components:
  schemas:
    ResponseModel:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
      required:
        - id
        - name
```

### OpenAPI Generation Guidelines

1. **Document all public endpoints**
2. **Include request/response schemas**
3. **Document error responses**
4. **Add examples where helpful**
5. **Keep descriptions concise but complete**

---

## Docstring Guidelines

### Python (Google Style)

```python
def function_name(param1: type, param2: type) -> return_type:
    """Brief one-line description.

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
    """Brief one-line description.

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

---

## Incremental Update Philosophy

**Update what changed, don't rewrite everything.**

### When Adding New Code

- Add docstrings to new public functions/classes
- Update README if public API expanded
- Add CLAUDE.md if new directory created
- Update OpenAPI spec if new endpoints

### When Modifying Code

- Update docstrings if behavior changed
- Update README usage examples if interface changed
- Update CLAUDE.md if file purposes changed
- Update OpenAPI spec if endpoints modified

### When Deleting Code

- Remove references from CLAUDE.md
- Update README if public features removed
- Remove endpoints from OpenAPI spec

---

## Output Requirements

Generate documentation as specified in analysis:

1. **README Updates**
   - Add missing sections using template
   - Update existing sections with current info
   - Maintain consistent formatting

2. **CLAUDE.md Files**
   - Create at project root if missing
   - Create in subdirectories as needed
   - Update existing files with changes

3. **OpenAPI Spec** (if applicable)
   - Create spec file if endpoints exist
   - Add new endpoint documentation
   - Update schemas for modified endpoints

4. **Code Docstrings**
   - Add to all public functions/classes
   - Update where behavior changed
   - Include type hints where missing

---

## TDD Cycle Complete

After DOC phase:
- Code is tested (RED-GREEN verified)
- Code is clean (REFACTOR completed)
- Code is documented (DOC completed)
  - README is complete and accurate
  - CLAUDE.md files exist where needed
  - OpenAPI spec current (if applicable)
  - Code has appropriate docstrings
- Ready for review/commit
