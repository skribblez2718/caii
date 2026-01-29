# TDD DOC Phase: Analysis

## Context

Analyze what documentation needs to be added or updated based on
the changes made during RED-GREEN-REFACTOR.

---

## Pre-Requisite: Runtime Verification

**BEFORE** analyzing documentation needs, verify the artifact runs correctly.

Reference: `runtime_check.md` for verification procedures by artifact type.

| Artifact Type | Verification |
|---------------|--------------|
| Library/Module | Import test |
| Script | Help flag test |
| Web App | Health endpoint test |
| CLI Tool | Help/version test |

**Gate:** Runtime check must PASS before proceeding to documentation.

---

## Focus Areas

1. **Code Documentation**
   - Function/method docstrings
   - Class docstrings
   - Module docstrings
   - Type hints (if not already added)

2. **Test Documentation**
   - Test docstrings explaining purpose
   - Test naming clarity

3. **External Documentation**
   - README updates (if public API changed)
   - CHANGELOG updates
   - API documentation

4. **Internal Documentation**
   - CLAUDE.md updates (if applicable)
   - Architecture notes (if significant)

## Analysis Checklist

- [ ] Identified undocumented functions
- [ ] Checked docstring completeness
- [ ] Reviewed test clarity
- [ ] Assessed external doc needs

## Scope Limitations

Documentation should be:
- Accurate (matches actual behavior)
- Concise (no excessive detail)
- Useful (helps future developers)

Do NOT:
- Document obvious code
- Write essays in docstrings
- Document implementation details that may change

## Output Focus

Provide documentation plan:
- List of items needing docstrings
- External docs to update
- Priority order
