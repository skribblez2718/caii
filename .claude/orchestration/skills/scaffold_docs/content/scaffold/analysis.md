# Scaffold-Docs Analysis Agent Task

You are the **analysis** agent for the scaffold-docs skill. Your task is to analyze the project structure and identify patterns for documentation generation.

## Context

- **Target Path:** {{ target_path }}
- **Detected Language:** {{ detected_language }}
- **Mode:** scaffold (creating new documentation)

## Your Mission

Analyze the project to understand:

### 1. Directory Structure Analysis

Examine the project structure and identify:
- Source code directories
- Test directories (if any)
- Configuration files
- Build artifacts directories
- Documentation directories (existing)

Create a clean directory tree representation (max 15 lines).

### 2. Key File Identification

Identify the most important files:
- Entry points (main.py, index.ts, etc.)
- Configuration files (package.json, pyproject.toml, etc.)
- Test configuration
- Existing documentation

### 3. Pattern Detection

Look for:
- Import patterns used in the codebase
- Naming conventions followed
- Test patterns (if tests exist)
- Framework-specific patterns

### 4. Documentation Gaps

Identify what documentation exists and what's missing:
- [ ] CLAUDE.md (root)
- [ ] .claude/rules/general.md
- [ ] docs/README.md
- [ ] docs/getting-started.md
- [ ] API documentation

## Output Format

Write your findings to the memory file in this format:

```markdown
## Section 1: Core Identity

### Project Analysis Summary
- **Language:** {{ detected_language }}
- **Frameworks:** [detected frameworks]
- **Build System:** [build tool]
- **Package Manager:** [package manager]

### Directory Structure
```
[clean directory tree - max 15 lines]
```

### Key Files
| File | Purpose | Priority |
|------|---------|----------|
| [path] | [description] | [high/medium/low] |

## Section 2: Analysis Findings

### Detected Patterns
- **Import Style:** [absolute/relative/mixed]
- **Naming Convention:** [snake_case/camelCase/etc]
- **Test Pattern:** [pytest/jest/etc]

### Documentation Status
| Document | Status | Notes |
|----------|--------|-------|
| CLAUDE.md | missing/exists | [notes] |
| .claude/rules/general.md | missing/exists | [notes] |
| docs/README.md | missing/exists | [notes] |
| docs/getting-started.md | missing/exists | [notes] |

### Recommendations
- [recommendation 1]
- [recommendation 2]

## Section 3: Downstream Directives

### For Synthesis Agent
- Directory tree for CLAUDE.md: [tree representation]
- Key files for documentation: [list]
- Commands to document: [inferred from package.json/Makefile/etc]
- Constraints based on patterns: [list]
- Files to create: [list of documentation files needed]

## Section 4: Open Questions

[Questions for user if any critical information is missing]
```

## Analysis Protocol

1. Use Glob to understand directory structure
2. Use Read to examine key configuration files
3. Use Grep to identify patterns (import styles, naming)
4. Synthesize findings into actionable documentation plan
