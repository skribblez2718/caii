# Scaffold-Docs Update Analysis Agent Task

You are the **analysis** agent for the scaffold-docs skill in UPDATE mode. Your task is to analyze what has changed in the project and identify documentation that needs updating.

## Context

- **Target Path:** {{ target_path }}
- **Detected Language:** {{ detected_language }}
- **Mode:** update (updating existing documentation)

## Your Mission

Analyze the project to identify documentation gaps and outdated content.

### 1. Existing Documentation Inventory

Read and analyze existing documentation:
- `{{ target_path }}/CLAUDE.md` - current state
- `{{ target_path }}/.claude/rules/general.md` - if exists
- `{{ target_path }}/docs/` - all markdown files

### 2. Codebase Changes Detection

Compare documentation against actual codebase:
- Are all commands in Quick Reference still valid?
- Are all files in Key Files table still present?
- Has the directory structure changed significantly?
- Are there new important files not documented?

### 3. Best Practices Compliance Check

Verify existing documentation follows best practices:
- Is CLAUDE.md under 100 lines?
- Does rules file have valid YAML frontmatter?
- Are there code snippets that should be file:line references?

### 4. Gap Analysis

Identify what's missing:
- New files needing documentation
- New commands needing documentation
- Changed patterns needing documentation update

## Output Format

Write your findings to the memory file in this format:

```markdown
## Section 1: Core Identity

### Documentation Inventory
| Document | Status | Last Modified |
|----------|--------|---------------|
| CLAUDE.md | exists/missing | [date if known] |
| .claude/rules/general.md | exists/missing | [date if known] |
| docs/README.md | exists/missing | [date if known] |
| docs/getting-started.md | exists/missing | [date if known] |

### Current CLAUDE.md Analysis
- **Line count:** [number]
- **Compliant (< 100):** yes/no
- **Sections present:** [list]

## Section 2: Change Analysis

### Files Added (not documented)
| File | Purpose | Priority |
|------|---------|----------|
| [path] | [description] | [high/medium/low] |

### Files Removed (but still documented)
| File | Current Doc Reference |
|------|----------------------|
| [path] | [where referenced] |

### Commands Changed
| Command | Doc Status | Current State |
|---------|------------|---------------|
| [cmd] | [outdated/missing] | [actual command] |

### Structure Changes
- [change 1]
- [change 2]

## Section 3: Downstream Directives

### For Synthesis Agent
Update required for:
- [ ] CLAUDE.md - [reason]
- [ ] .claude/rules/general.md - [reason]
- [ ] docs/README.md - [reason]
- [ ] docs/getting-started.md - [reason]

### Specific Updates Needed
1. [specific update instruction]
2. [specific update instruction]

### Preserve (Do Not Modify)
- [user-added content to preserve]

## Section 4: Open Questions

[Questions about unclear changes]
```

## Analysis Protocol

1. Read existing CLAUDE.md and extract current documentation
2. Compare documented files against actual filesystem
3. Verify commands are still valid
4. Identify gaps between documentation and reality
5. Prioritize updates by impact
