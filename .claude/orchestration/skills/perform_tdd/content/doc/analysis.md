# TDD DOC Phase: Analysis

## Context

Analyze what documentation needs to be added or updated based on
the changes made during RED-GREEN-REFACTOR. This phase ensures
production-grade documentation on every TDD cycle.

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

## Documentation Detection Checklist

### 1. README Completeness

Check if project README exists and contains ALL required sections:

| Section | Status | Notes |
|---------|--------|-------|
| **Description** | ☐ | What the project does, key features |
| **Installation/Setup** | ☐ | Dependencies, environment setup, configuration |
| **Usage** | ☐ | Basic usage examples, common workflows |
| **Testing** | ☐ | How to run tests, coverage requirements |
| **API Reference** | ☐ | Link to OpenAPI spec (if applicable) |
| **Contributing** | ☐ | Development workflow, PR process |
| **License** | ☐ | License type and link |

**Missing sections?** → Flag for generation phase.

### 2. CLAUDE.md Coverage

Check for CLAUDE.md presence in relevant directories:

| Location | Required When | Status |
|----------|---------------|--------|
| Project root | Always | ☐ |
| `src/` or main code dir | Always for code dirs | ☐ |
| Each major subdirectory | Contains distinct functionality | ☐ |
| `tests/` | Test infrastructure exists | ☐ |

**CLAUDE.md Purpose:**
- Architecture overview (at root)
- Purpose and key files (in subdirs)
- Patterns and conventions used
- Quick reference for AI assistants

**Missing CLAUDE.md files?** → Flag for generation phase.

### 3. OpenAPI Spec (API Projects Only)

Check if project has HTTP endpoints:

| Indicator | Check |
|-----------|-------|
| Framework imports | Flask, FastAPI, Express, Django REST |
| Route decorators | `@app.route`, `@router.get`, etc. |
| HTTP handlers | Functions handling request/response |
| Existing spec | `openapi.yaml`, `swagger.json`, `docs/api.*` |

**If API endpoints exist:**
- [ ] OpenAPI spec exists at standard location
- [ ] Spec is version 3.0+
- [ ] All endpoints documented
- [ ] Request/response schemas defined

**Missing or outdated spec?** → Flag for generation phase.

---

## Code Documentation Focus Areas

1. **Function/Method Docstrings**
   - Public functions without docstrings
   - Docstrings that don't match current behavior
   - Missing parameter/return descriptions

2. **Class Docstrings**
   - Classes without purpose description
   - Missing attribute documentation
   - Outdated usage examples

3. **Module Docstrings**
   - Files without module-level docstrings
   - Incorrect module descriptions

4. **Type Hints**
   - Functions missing type annotations
   - Incorrect or outdated types

---

## Incremental Update Scope

Each TDD cycle should check documentation **incrementally**, not rewrite everything:

### What Changed This Cycle?

| Changed | Documentation Impact |
|---------|---------------------|
| New function/class | Add docstring |
| Modified signature | Update docstring params |
| New test file | Update testing section |
| New API endpoint | Update OpenAPI spec |
| New subdirectory | Consider CLAUDE.md |
| Public API change | Update README usage |

### What to Skip

- Unchanged files (existing docs still valid)
- Internal/private functions (unless complex)
- Test helper functions (unless reusable)
- Generated code documentation

---

## Analysis Checklist

- [ ] README sections audit completed
- [ ] CLAUDE.md coverage checked
- [ ] OpenAPI spec status determined (if applicable)
- [ ] Undocumented public functions identified
- [ ] Docstring accuracy verified for changed code
- [ ] Test documentation reviewed
- [ ] External doc update needs assessed

---

## Scope Limitations

Documentation should be:
- **Accurate** - Matches actual behavior
- **Concise** - No excessive detail
- **Useful** - Helps future developers and AI assistants
- **Maintained** - Updated with code changes

Do NOT:
- Document obvious code
- Write essays in docstrings
- Document implementation details that may change
- Create documentation for documentation's sake

---

## Output Focus

Provide documentation plan with:

1. **README Updates Needed**
   - Missing sections to add
   - Sections to update

2. **CLAUDE.md Files Needed**
   - Directories requiring new files
   - Existing files to update

3. **OpenAPI Spec Actions** (if applicable)
   - New endpoints to document
   - Schema updates needed

4. **Code Documentation**
   - List of items needing docstrings
   - Priority order (public API first)

5. **Priority Order**
   - Critical: README, CLAUDE.md at root
   - High: Public API docstrings, OpenAPI spec
   - Medium: Internal documentation
   - Low: Nice-to-have improvements
