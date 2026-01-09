# develop-command

Composite skill for creating and managing Claude Code slash commands.

## Phases

| Phase | Name | Atomic Skill |
|-------|------|--------------|
| 0 | Requirements Clarification | orchestrate-clarification |
| 1 | Command Generation | orchestrate-generation |
| 2 | Command Validation | orchestrate-validation |

## When Used

- Creating new utility commands
- Adding commands to existing categories
- Building composite commands that call other commands
- Updating existing commands

## Key Outputs

- Command definition file (`.claude/commands/{category}/{name}.md`)
- Updated DA.md Utility Commands section

## Phase Config Location

`../config.py` → `DEVELOP_COMMAND_PHASES`

## Command File Structure

```markdown
---
description: Brief description
---

Explanation of command.

```bash
# Command implementation
echo "Complete"
```
```
