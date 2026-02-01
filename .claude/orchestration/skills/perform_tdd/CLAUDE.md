# perform-tdd Skill Orchestration

Python-based orchestration for Test-Driven Development workflow.

---

## Directory Structure

```
skills/perform_tdd/
├── __init__.py           # Package exports
├── CLAUDE.md             # This file
├── tdd_state.py          # TDDPhase, TDDFSM, TDDState
├── flows.py              # Agent flow definitions
├── entry.py              # Main entry point (triggers agent flows)
├── advance.py            # Phase advancement
├── complete.py           # Session completion
├── content/
│   ├── phase_red.md      # RED phase prompt (legacy)
│   ├── phase_green.md    # GREEN phase prompt (legacy)
│   ├── phase_refactor.md # REFACTOR phase prompt (legacy)
│   ├── phase_doc.md      # DOC phase prompt (legacy)
│   ├── red/              # Agent-specific content for RED
│   │   ├── clarification.md
│   │   ├── research.md
│   │   ├── analysis.md
│   │   └── generation.md
│   ├── green/            # Agent-specific content for GREEN
│   │   ├── analysis.md
│   │   ├── generation.md
│   │   └── validation.md
│   ├── refactor/         # Agent-specific content for REFACTOR
│   │   ├── analysis.md
│   │   ├── generation.md
│   │   └── validation.md
│   └── doc/              # Agent-specific content for DOC
│       ├── analysis.md
│       └── generation.md
└── state/                # Runtime state files (gitignored)
```

---

## Agent Flow Architecture

Each TDD phase now triggers an agent flow:

```
         RED Phase
    ┌─────────────────┐
    │  clarification  │ (conditional - if requirements unclear)
    │       ↓         │
    │    research     │ (find test patterns)
    │       ↓         │
    │    analysis     │ (decompose into test cases)
    │       ↓         │
    │   generation    │ (write failing test)
    └─────────────────┘

        GREEN Phase
    ┌─────────────────┐
    │    analysis     │ (understand failing test)
    │       ↓         │
    │   generation    │ (write minimal impl)
    │       ↓         │
    │   validation    │ (verify tests pass)
    └─────────────────┘

      REFACTOR Phase
    ┌─────────────────┐
    │    analysis     │ (identify improvements)
    │       ↓         │
    │   generation    │ (apply refactoring)
    │       ↓         │
    │   validation    │ (verify tests still pass)
    └─────────────────┘

        DOC Phase
    ┌─────────────────┐
    │    analysis     │ (identify doc needs)
    │       ↓         │
    │   generation    │ (write documentation)
    └─────────────────┘
```

---

## Flow Definitions (flows.py)

| Flow | Flow ID | Agents |
|------|---------|--------|
| `TDD_RED_FLOW` | `perform-tdd-red` | clarification → research → analysis → generation |
| `TDD_GREEN_FLOW` | `perform-tdd-green` | analysis → generation → validation |
| `TDD_REFACTOR_FLOW` | `perform-tdd-refactor` | analysis → generation → validation |
| `TDD_DOC_FLOW` | `perform-tdd-doc` | analysis → generation |

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

Creates new or loads existing TDD session and triggers agent flow:

```bash
# Full flow mode (triggers agents)
python3 entry.py --algorithm-state {alg_id} [--perform-tdd-state {tdd_id}] [--target file] [--test file]

# Legacy mode (just prints phase content)
python3 entry.py --algorithm-state {alg_id} --no-flow
```

### advance.py

Advances to next phase and triggers agent flow for that phase:

```bash
# Full flow mode (triggers agents for next phase)
python3 advance.py --perform-tdd-state {tdd_id} [--output '{"key": "value"}']

# Legacy mode (just prints phase content)
python3 advance.py --perform-tdd-state {tdd_id} --no-flow
```

**Note:** `advance.py` now uses `invoke_agent_flow()` from `flow_invoker.py` to trigger agent chains, ensuring consistent flow invocation across entry points.

**Phase Advancement Gate:** Before advancing to the next phase, `advance.py` validates
that the current phase's agent flow has completed all agents using `is_flow_complete()`.
This prevents premature phase advancement when agents haven't all run.

```python
if not is_flow_complete(state.session_id, flow.flow_id):
    print("ERROR: Cannot advance - flow not complete")
    sys.exit(1)
```

### complete.py

Completes session or loops back:

```bash
python3 complete.py --perform-tdd-state {tdd_id} [--loop-back]
```

---

## Agent Memory Files

Each agent in the flow creates a memory file:

```
.claude/memory/{session_id}-{agent}-memory.md
```

Example for RED phase:
- `abc123-clarification-memory.md`
- `abc123-research-memory.md`
- `abc123-analysis-memory.md`
- `abc123-generation-memory.md`

---

## Critical Invariants

```
⚠️  INVARIANTS - VIOLATING THESE BREAKS THE SYSTEM

1. Learning Injection is MANDATORY
   └→ Each agent has MANDATORY section at end of .md file
   └→ Agents scan their learnings before work

2. Memory file MUST exist before agent completes
   └→ Verified by agent_complete()
   └→ Section 3 (Downstream Directives) feeds next agent

3. ALWAYS save state BEFORE printing any directive
   └→ state.save() before print()

4. Agent chains via directive, NOT via DA hub-and-spoke
   └→ Agent prints next agent directive
   └→ DA just executes what it sees
```

---

## Tests

Located at: `tests/unit/orchestration/skills/perform_tdd/`

- `test_tdd_state.py` - TDDPhase, TDDState tests
- `test_tdd_fsm.py` - TDDFSM transition tests
- `test_entry.py` - Entry point tests

Run tests:

```bash
cd .claude/orchestration
source .venv/bin/activate
pytest tests/unit/orchestration/skills/perform_tdd/ -v
```

---

*Last updated: 2026-01-31*
