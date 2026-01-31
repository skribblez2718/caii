# CAII - Cognitive AI Infrastructure

Multi-agent orchestration system for Claude Code implementing The Last Algorithm.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/perform-tdd` | Execute TDD workflow (RED-GREEN-REFACTOR-DOC) |
| `/clean:all` | Clean all state, research, plan, and memory files |
| `make test` | Run tests (in `.claude/orchestration/` venv) |
| `make lint` | Run linting |

## Documentation

Context-specific documentation auto-loads from `.claude/rules/` when working in matching paths:

| Rule File | Applies To |
|-----------|------------|
| `rules/general.md` | All work (always loaded) |
| `rules/orchestration/agents.md` | `.claude/agents/**` |
| `rules/orchestration/skills.md` | `.claude/skills/**`, `.claude/orchestration/skills/**` |
| `rules/orchestration/inner-loop.md` | `.claude/orchestration/inner_loop/**` |
| `rules/orchestration/outer-loop.md` | `.claude/orchestration/outer_loop/**` |
| `rules/orchestration/decompose.md` | `.claude/orchestration/decompose/**` |
| `rules/memory/workflows.md` | `.claude/memory/**` |

Run `/memory` to see currently loaded context.

For full system architecture diagram, see `.claude/docs/architecture.md`.

## Critical Constraints

- **NEVER** create projects inside `${CAII_DIRECTORY}` - use `${PROJECT_ROOT}`
- Use absolute imports only (never relative)
- Type hints required on all Python functions
- All code changes MUST use `/perform-tdd`

## System Architecture

```
.claude/
├── agents/         # 7 cognitive agent definitions
├── commands/       # Slash commands (clean:*, etc.)
├── docs/           # Reference documentation (architecture.md)
├── hooks/          # Orchestration hooks
├── learnings/      # Agent-specific learnings
├── memory/         # Workflow memory files (gitignored)
├── orchestration/  # Python orchestration system
├── plans/          # Plan files (gitignored)
├── research/       # Research documents
├── rules/          # Path-scoped documentation
└── skills/         # Skill definitions
```

## Key Files

| File | Purpose |
|------|---------|
| `.claude/DA.md` | DA system prompt (loaded via hook) |
| `.claude/settings.json` | Environment and hook configuration |
| `.claude/orchestration/CLAUDE.md` | Full orchestration index |
| `.claude/docs/architecture.md` | The Last Algorithm flow diagram |

---
*Last updated: 2026-01-31*
