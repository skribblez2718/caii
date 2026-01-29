# TDD REFACTOR Phase: Validation

## Context

Validate that refactoring maintained behavior, improved quality, AND integration
tests pass (if applicable).

---

## Gate Criteria (ALL REQUIRED)

### Gate 1: All Tests Pass
```bash
pytest {test_directory} -v --tb=short
```
**FAIL if:** Any test fails

### Gate 2: Lint Score
```bash
pylint {module} --score=yes
```
**FAIL if:** Score < 9.0/10 (or decreased from before)

### Gate 3: Format Check
```bash
black --check {files}
```
**FAIL if:** Would make changes

### Gate 4: Type Check
```bash
mypy {module} --ignore-missing-imports
```
**FAIL if:** Any type errors

### Gate 5: Integration Tests (if exist)
```bash
pytest -m integration -v --tb=short
```
**PASS if:** No integration tests exist OR all pass

### Gate 6: Docstring Check
```bash
pydocstyle {module} --convention=google
```
**FAIL if:** Missing or malformed docstrings

---

## Quality Improvement Checklist

- [ ] Code smells addressed
- [ ] Duplication reduced
- [ ] Naming improved
- [ ] Complexity reduced

---

## Output

Provide verdict with lint score comparison:
- **GO:** All gates pass, quality improved → Proceed to DOC
- **NO-GO:** Issues found → Return to ANALYSIS/GENERATION

Report format:
```
Gate 1 (Tests): PASS/FAIL
Gate 2 (Lint): PASS/FAIL - Score: X.X/10 (before: Y.Y/10)
Gate 3 (Format): PASS/FAIL
Gate 4 (Type): PASS/FAIL - {error count if any}
Gate 5 (Integration): PASS/SKIP/FAIL
Gate 6 (Docstring): PASS/FAIL - {error count if any}

Verdict: GO / NO-GO
```
