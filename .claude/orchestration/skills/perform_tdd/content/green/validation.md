# TDD GREEN Phase: Validation

## Context

Validate implementation makes all tests pass AND meets quality gates.
**All checks are BLOCKING** - failures prevent advancement to REFACTOR.

---

## Gate Criteria (ALL REQUIRED)

### Gate 1: Tests Pass
```bash
pytest {test_file} -v --tb=short
```
**FAIL if:** Any test fails

### Gate 2: Import Verification
```bash
python -c "from {module_path} import *"
```
**FAIL if:** ImportError, NameError (catches undefined variables)

### Gate 3: Lint Errors (Blocking)
```bash
pylint {implementation_file} --errors-only --disable=C,R,W
```
**FAIL if:** Any E-level errors (undefined names, bad imports)

### Gate 4: Type Check (Blocking)
```bash
mypy {implementation_file} --ignore-missing-imports --no-error-summary
```
**FAIL if:** Any type errors (catches undefined names, wrong types)

### Gate 5: Syntax Validation
```bash
python -m py_compile {implementation_file}
```
**FAIL if:** Syntax errors

---

## Validation Checklist

- [ ] All tests pass (Gate 1)
- [ ] No import errors (Gate 2)
- [ ] No lint errors (Gate 3)
- [ ] No type errors (Gate 4)
- [ ] No syntax errors (Gate 5)
- [ ] Implementation is minimal (no extra features)

---

## Output

**GO:** All gates pass → Proceed to REFACTOR
**NO-GO:** Any gate fails → Return to GENERATION with specific failure

Report format:
```
Gate 1 (Tests): PASS/FAIL
Gate 2 (Import): PASS/FAIL
Gate 3 (Lint): PASS/FAIL - {error count if any}
Gate 4 (Type): PASS/FAIL - {error count if any}
Gate 5 (Syntax): PASS/FAIL

Verdict: GO / NO-GO
```
