---
paths:
  - ".claude/skills/**"
  - ".claude/orchestration/skills/**"
---

# Skill Development Guidelines

## Skill Types

| Type | Description | Location |
|------|-------------|----------|
| **Composite** | Multi-phase workflows with multiple agents | `.claude/skills/{skill-name}/` |
| **Atomic** | Single-agent wrappers | `.claude/skills/orchestrate-*/` |

## Available Composite Skills

| Skill | Purpose | Semantic Triggers |
|-------|---------|-------------------|
| **perform-tdd** | TDD cycle (RED-GREEN-REFACTOR-DOC) | implement, fix bug, write code, refactor |
| **develop-skill** | Create/modify workflow skills | create skill, new skill, modify workflow |
| **develop-learnings** | Capture workflow learnings | capture learnings, document insights |
| **develop-command** | Create slash commands | create command, slash command |

## Skill Directory Structure

```
.claude/skills/{skill-name}/
├── SKILL.md              # Skill definition and metadata
└── resources/            # Skill-specific resources
    ├── patterns.md
    └── workflow.md

.claude/orchestration/skills/{skill_name}/
├── CLAUDE.md             # Orchestration index
├── entry.py              # Skill entry point
├── flows.py              # AgentFlow definitions
├── *_state.py            # Skill-specific state
└── content/              # Phase content files
    └── phase_{name}.md
```

## Skill Definition (SKILL.md)

```markdown
---
name: {skill-name}
description: "{description}"
phases: [{phase1}, {phase2}, ...]
triggers: ["{semantic trigger 1}", "{trigger 2}"]
---

# {Skill Name}

## Overview
## Phases
## Usage
```

## Skill Selection Guide

```
Does task match a composite skill pattern?
├── YES → Use matching composite skill
└── NO → Does task require cognitive work?
         ├── YES → Dynamic skill sequencing with atomic skills
         └── NO → Single atomic skill
```

## perform-tdd Invocation

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/entry.py --algorithm-state {session_id}
```

## TDD Phase Gates

| Phase | Requirement |
|-------|-------------|
| **RED** | Test exists AND fails |
| **GREEN** | All tests pass |
| **REFACTOR** | Tests pass + `make lint` = 10/10 |
| **DOC** | Documentation updated |

## Atomic Skills (orchestrate-*)

| Skill | Agent | When to Use |
|-------|-------|-------------|
| `orchestrate-clarification` | clarification | Ambiguity resolution |
| `orchestrate-research` | research | Knowledge gaps |
| `orchestrate-analysis` | analysis | Complexity decomposition |
| `orchestrate-synthesis` | synthesis | Integration of findings |
| `orchestrate-generation` | generation | Artifact creation |
| `orchestrate-validation` | validation | Quality verification |
| `orchestrate-memory` | memory | Progress tracking |
