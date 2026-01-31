# CAII General Guidelines

These guidelines apply to all work in the CAII (Cognitive AI Infrastructure) project.

## Critical Constraints

| Constraint | Rule |
|------------|------|
| **Project Creation** | NEVER create projects inside `${CAII_DIRECTORY}` - use `${PROJECT_ROOT}` |
| **Imports** | Use absolute imports only - NEVER relative imports |
| **Type Hints** | Required on ALL Python functions |
| **TDD** | All code changes MUST use the `/perform-tdd` skill |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `${PROJECT_ROOT}` | Where new projects are created |
| `${CAII_DIRECTORY}` | System architecture root (`.claude/` parent) |

## Common Commands

| Command | Purpose |
|---------|---------|
| `/clean:all` | Clean all state files |
| `/perform-tdd` | Execute TDD workflow |
| `make test` | Run tests (in orchestration venv) |
| `make lint` | Run linting |
| `make format` | Format code |

## Test Locations

Tests are located in `.claude/orchestration/tests/unit/` mirroring source structure.

## Python Coding Standards

**Target Version:** Python 3.11+

```python
# CORRECT - absolute imports
from orchestration.outer_loop.gather import entry

# WRONG - never use relative imports
from .outer_loop.gather import entry  # FORBIDDEN
```

## File Naming Conventions

| Type | Pattern |
|------|---------|
| Entry points | `entry.py` |
| State files | `*_state.py` |
| FSM definitions | `*_fsm.py` |
| Memory files | `.claude/memory/{task_id}-{agent}-memory.md` |
| Learnings | `.claude/learnings/{agent}/*.md` |
