# develop-learnings

Transform completed workflow experiences into structured, reusable learnings.

## Phases

| Phase | Name | Atomic Skill |
|-------|------|--------------|
| 1 | Discovery | orchestrate-analysis |
| 2 | Per-Function Authoring | ITERATIVE (all 6 agents) |
| 2.5 | Integration Analysis | orchestrate-synthesis |
| 3 | Consolidation | orchestrate-synthesis |
| 4 | Validation | orchestrate-validation (REMEDIATION) |
| 5 | Commit | orchestrate-generation |
| 5.5 | Post-Integration Cleanup | orchestrate-analysis |

## When Used

- Post-workflow capture of insights
- Converting unknown→known knowledge
- Preserving patterns and anti-patterns

## Learning Types

- Heuristics
- Anti-patterns
- Checklists
- Domain snippets

## Output Locations

- `.claude/learnings/{cognitive-function}/heuristics.md`
- `.claude/learnings/{cognitive-function}/anti-patterns.md`
- `.claude/learnings/{cognitive-function}/checklists.md`

## Phase Config Location

`../config.py` → `DEVELOP_LEARNINGS_PHASES`
