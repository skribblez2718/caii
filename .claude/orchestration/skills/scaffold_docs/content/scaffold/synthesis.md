# Scaffold-Docs Synthesis Agent Task

You are the **synthesis** agent for the scaffold-docs skill. Your task is to generate the documentation files based on gathered information.

## Context

- **Target Path:** {{ target_path }}
- **Detected Language:** {{ detected_language }}
- **Mode:** scaffold (creating new documentation)

## Your Mission

Create the following documentation files:

### 1. CLAUDE.md (Root)

Create `{{ target_path }}/CLAUDE.md` with:
- Project name and description
- Quick reference commands table
- Documentation table (if .claude/rules/ exists)
- Critical constraints (4-5 bullet points)
- System architecture tree (from analysis)
- Key files table

**CRITICAL:** Keep under 100 lines total.

### 2. .claude/rules/general.md

Create `{{ target_path }}/.claude/rules/general.md` with:
- YAML frontmatter with globs and alwaysApply: true
- Critical constraints table
- Environment variables (if applicable)
- Common commands table
- Test locations
- Language-specific coding standards
- File naming conventions

### 3. docs/README.md

Create `{{ target_path }}/docs/README.md` with:
- Project name and description
- Quick links to other docs
- Overview section
- Installation instructions
- Usage example
- Project structure
- Contributing section
- License section

### 4. docs/getting-started.md

Create `{{ target_path }}/docs/getting-started.md` with:
- Prerequisites
- Installation steps
- Configuration (if needed)
- Quick start commands
- Next steps

## Output Format

Write your findings to the memory file in this format:

```markdown
## Section 1: Core Identity

### Files Generated
| File | Lines | Status |
|------|-------|--------|
| CLAUDE.md | [count] | created |
| .claude/rules/general.md | [count] | created |
| docs/README.md | [count] | created |
| docs/getting-started.md | [count] | created |

## Section 2: Synthesis Results

### CLAUDE.md Summary
- Total lines: [must be < 100]
- Commands documented: [count]
- Constraints listed: [count]

### Rules File Summary
- YAML frontmatter: valid
- Sections included: [list]

### User Docs Summary
- README.md sections: [list]
- getting-started.md sections: [list]

## Section 3: Downstream Directives

### For Validation Agent
- Files to validate:
  - `{{ target_path }}/CLAUDE.md` - must be < 100 lines
  - `{{ target_path }}/.claude/rules/general.md` - must have valid YAML frontmatter
  - `{{ target_path }}/docs/README.md` - must exist
  - `{{ target_path }}/docs/getting-started.md` - must exist

### Validation Criteria
- [ ] CLAUDE.md under 100 lines
- [ ] YAML frontmatter in general.md is valid
- [ ] All referenced files in Key Files table exist
- [ ] Commands in Quick Reference are accurate

## Section 4: Open Questions

[None - synthesis complete]
```

## Synthesis Protocol

1. Read clarification and analysis memory files for context
2. Create directories if needed (`mkdir -p`)
3. Generate each file using Write tool
4. Ensure CLAUDE.md is under 100 lines
5. Use proper YAML frontmatter in rules files
