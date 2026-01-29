# TDD DOC Phase - Update Documentation

**Session:** {session_id} | **Cycle:** {cycle_count} | **Target:** {target_file} | **Test:** {test_file}

---

## CRITICAL: Virtual Environment

**BEFORE running any test or Python commands:**

1. **Locate venv:** Usually in project root (`.venv/`), but may be elsewhere:
   - Check `.claude/orchestration/.venv/` for CAII-style projects
   - Scan for `.venv/` or `venv/` directories if not in root

2. **Activate:** `source /path/to/.venv/bin/activate`

3. **Verify dependencies:** If `pytest` or other tools fail, install them:
   ```bash
   pip install pytest black pylint mypy pytest-cov
   ```

**NEVER run tests without activated virtual environment.**

---

## Objective

Update documentation to reflect code changes.

## Gate Requirement

**Documentation MUST be updated** AND **accurate** before completing cycle.

## Agent Orchestration

1. **analysis**: Identify documentation gaps (docstrings, README, CLAUDE.md)
2. **generation**: Update documentation
3. **validation**: Verify accuracy and completeness

## Documentation Checklist

### Code Documentation

- [ ] **Docstrings**: All public functions/classes have docstrings
- [ ] **Type hints**: All function signatures have type hints
- [ ] **Examples**: Complex functions include usage examples

### Project Documentation

- [ ] **CLAUDE.md**: Updated if architecture changed
- [ ] **README.md**: Updated if public API changed
- [ ] **Inline comments**: Added where logic isn't self-evident

### Documentation Quality

| Check | Criteria |
|-------|----------|
| Accurate | Matches actual behavior |
| Complete | All public APIs documented |
| Concise | No unnecessary verbosity |
| Current | Reflects latest changes |

---

## Verification

Review documentation changes:

1. Docstrings match function behavior
2. Type hints are accurate
3. Examples are runnable
4. No stale/outdated information

---

## Complete or Loop Back

### Complete TDD Session

If no more features to add:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/skills/tdd/complete.py --tdd-state {session_id}
```

### Loop Back for Next Feature

If more features needed:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/skills/tdd/complete.py --tdd-state {session_id} --loop-back
```

This starts a new RED-GREEN-REFACTOR-DOC cycle.
