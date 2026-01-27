# TDD Skill Orchestration

Python-based orchestration for Test-Driven Development workflow.

---

## Directory Structure

```
skills/tdd/
├── __init__.py           # Package exports
├── CLAUDE.md             # This file
├── tdd_state.py          # TDDPhase, TDDFSM, TDDState
├── entry.py              # Main entry point
├── advance.py            # Phase advancement
├── complete.py           # Session completion
├── content/
│   ├── phase_red.md      # RED phase prompt
│   ├── phase_green.md    # GREEN phase prompt
│   ├── phase_refactor.md # REFACTOR phase prompt
│   └── phase_doc.md      # DOC phase prompt
└── state/                # Runtime state files (gitignored)
```

---

## State Management

### TDDPhase Enum

```
INITIALIZED -> RED -> GREEN -> REFACTOR -> DOC -> COMPLETED
                ^                          |
                |_________(loop-back)______|
```

### TDDState Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | str | 12-char unique identifier |
| `parent_algorithm_id` | str | Link to parent AlgorithmState |
| `target_file` | str | Implementation file path |
| `test_file` | str | Test file path |
| `fsm` | TDDFSM | State machine |
| `phase_outputs` | Dict | Outputs recorded per phase |
| `cycle_count` | int | Number of completed TDD cycles |

### FSM Transitions

| From | To (valid) |
|------|------------|
| INITIALIZED | RED |
| RED | GREEN |
| GREEN | REFACTOR |
| REFACTOR | DOC |
| DOC | COMPLETED, RED (loop-back) |
| COMPLETED | (terminal) |

---

## Entry Points

### entry.py

Creates new or loads existing TDD session:

```bash
python3 entry.py --algorithm-state {alg_id} [--tdd-state {tdd_id}] [--target file] [--test file]
```

### advance.py

Advances to next phase:

```bash
python3 advance.py --tdd-state {tdd_id} [--output '{"key": "value"}']
```

### complete.py

Completes session or loops back:

```bash
python3 complete.py --tdd-state {tdd_id} [--loop-back]
```

---

## Critical Invariant

**ALWAYS save state BEFORE printing any directive:**

```python
state.save()  # FIRST
print(directive)  # THEN
```

---

## Tests

Located at: `tests/unit/orchestration/skills/tdd/`

- `test_tdd_state.py` - TDDPhase, TDDState tests
- `test_tdd_fsm.py` - TDDFSM transition tests
- `test_entry.py` - Entry point tests

Run tests:

```bash
cd .claude/orchestration
source .venv/bin/activate
pytest tests/unit/orchestration/skills/tdd/ -v
```

---

*Last updated: 2026-01-27*
