---
name: scaffold-docs
description: "Initialize and maintain project documentation. Creates CLAUDE.md, .claude/rules/, and docs/ directory following best practices. Use for new projects or updating existing documentation."
disable-model-invocation: false
allowed-tools: Bash(ls:*, pwd, mkdir:*), Glob, Grep, Read, Write, Edit, Task
---

# scaffold-docs Skill

Create and maintain project documentation with two scopes:
1. **Claude Context** - CLAUDE.md + `.claude/rules/` (for Claude Code context)
2. **User Documentation** - `docs/` directory (for human readers)

---

## When to Use

- Creating a new project that needs documentation
- Initializing Claude Code context for an existing project
- Updating documentation after significant codebase changes
- Standardizing documentation across projects

## When NOT to Use

- Quick documentation fixes (edit directly instead)
- Projects with established custom documentation patterns
- Documentation that intentionally deviates from best practices

---

## MANDATORY EXECUTION

Execute immediately to start documentation scaffolding:

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/scaffold_docs/entry.py --algorithm-state {session_id}
```

### With Target Project Path

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/scaffold_docs/entry.py \
  --algorithm-state {session_id} \
  --target ${PROJECT_ROOT}/my-project
```

### Force Update Mode

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/scaffold_docs/entry.py \
  --algorithm-state {session_id} \
  --target ${PROJECT_ROOT}/my-project \
  --update
```

---

## Modes of Operation

| Mode | Trigger | Purpose |
|------|---------|---------|
| **Scaffold** | No CLAUDE.md exists | Create initial documentation structure |
| **Update** | CLAUDE.md exists | Regenerate/update existing documentation |

---

## Agent Flow

### SCAFFOLD_FLOW (create mode)

```
clarification → analysis → synthesis → validation
```

| Agent | Purpose |
|-------|---------|
| **clarification** | Gather project context, commands, constraints from user |
| **analysis** | Analyze codebase structure, detect patterns, identify key files |
| **synthesis** | Generate CLAUDE.md, rules/general.md, and docs/* files |
| **validation** | Verify files created, validate content, check best practices |

### UPDATE_FLOW (update mode)

```
analysis → synthesis → validation
```

| Agent | Purpose |
|-------|---------|
| **analysis** | Detect changes in codebase, identify outdated documentation |
| **synthesis** | Regenerate/update affected documentation files |
| **validation** | Verify updates, validate consistency |

---

## Generated Structure

### Claude Context (always created)

```
{project}/
├── CLAUDE.md                    # Root docs index (<100 lines)
└── .claude/
    └── rules/
        └── general.md           # Always-loaded guidelines
```

### User Documentation (always created)

```
{project}/
└── docs/
    ├── README.md               # Documentation index
    └── getting-started.md      # Quick start guide
```

---

## Best Practices Enforced

| Practice | Enforcement |
|----------|-------------|
| Root CLAUDE.md length | **Under 100 lines** |
| Path-specific context | Use `.claude/rules/` with YAML frontmatter |
| Code references | Use `file:line` not copied snippets |
| Content scope | Universally applicable content only |

---

## Language Detection

Auto-detects project language/framework:

| File Present | Detected Language |
|--------------|-------------------|
| `package.json` | Node.js/TypeScript |
| `pyproject.toml`, `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml`, `build.gradle` | Java |

---

## Resources

- `.claude/skills/scaffold-docs/resources/templates/` - Template files
- `.claude/research/claude-md-best-practices.md` - Best practices reference

---

## State Management

Sessions are tracked in:
- State files: `.claude/orchestration/skills/scaffold_docs/state/scaffold-docs-{session_id}.json`
- Linked to parent algorithm via `parent_algorithm_id`

Session state includes:
- Current mode (scaffold/update)
- Target path
- Detected language
- Created/updated files
