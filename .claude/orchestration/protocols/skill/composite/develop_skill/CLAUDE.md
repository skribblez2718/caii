# develop-skill

Meta-skill for creating and updating workflow skills in the Penny system.

## Phases

| Phase | Name | Atomic Skill |
|-------|------|--------------|
| 0 | Requirements Clarification | orchestrate-clarification |
| 0.5 | Atomic Provisioning | AUTO (no agent) |
| 0.6 | Composite Validation | AUTO (no agent) |
| 1 | Complexity Analysis | orchestrate-analysis |
| 1.5 | Pattern Research | orchestrate-research |
| 2 | Design Synthesis | orchestrate-synthesis |
| 3 | Skill Generation | orchestrate-generation |
| 4 | Skill Validation | orchestrate-validation |
| 5 | DA Registration | Direct execution |

## When Used

- Creating new workflow skills
- Modifying existing skills
- Any Penny system modifications (skills, agents, protocols)

## Key Outputs

- Skill definition file (SKILL.md or config entries)
- Updated DA.md registration
- Phase content files

## Phase Config Location

`../config.py` → `DEVELOP_SKILL_PHASES`
