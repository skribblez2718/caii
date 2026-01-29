# Pre-DOC Runtime Verification

## Context

Before documentation, verify the artifact actually RUNS correctly.
This catches runtime errors that tests might miss.

---

## Verification by Artifact Type

### Python Library/Module
```bash
# Verify import succeeds with no side effects
python -c "import {module}; print('Import OK')"
```

### Python Script
```bash
# Verify script runs without immediate crash
python {script} --help 2>/dev/null || python {script} -h 2>/dev/null || echo "No help flag"
```

### Web Application (Flask/FastAPI/Django)
```bash
# Start app, verify health, shutdown
timeout 10 bash -c '
  python {app_entry} &
  APP_PID=$!
  sleep 3

  # Check if process is running
  if ! kill -0 $APP_PID 2>/dev/null; then
    echo "FAIL: App crashed on startup"
    exit 1
  fi

  # Check health endpoint
  if curl -sf http://localhost:{port}/health > /dev/null; then
    echo "PASS: Health check OK"
  elif curl -sf http://localhost:{port}/ > /dev/null; then
    echo "PASS: Root endpoint OK"
  else
    echo "FAIL: No response from app"
    kill $APP_PID 2>/dev/null
    exit 1
  fi

  kill $APP_PID 2>/dev/null
  echo "PASS: Runtime verification complete"
'
```

### CLI Tool
```bash
# Verify basic operation
python {cli} --help && echo "PASS: Help works"
python {cli} --version 2>/dev/null && echo "PASS: Version works"
```

---

## Gate Criteria

**PASS:** Artifact runs without crashing
**FAIL:** Any runtime error (NameError, ImportError, etc.)

---

## Skip Conditions

Skip runtime verification if:
- Artifact is pure library code (no entry point)
- Tests already include E2E coverage with `@pytest.mark.e2e`

---

## Output

Report format:
```
Artifact Type: {library|script|web_app|cli}
Runtime Check: PASS/FAIL/SKIP
Details: {specific output or skip reason}

Verdict: GO / NO-GO
```
