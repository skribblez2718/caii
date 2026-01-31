# Decompose Protocol

Breaks complex/very_complex tasks into SIMPLE subtasks using agent orchestration.

---

## Purpose

When a task is classified as `complex` or `very_complex` by complexity analysis, it routes here instead of directly to GATHER. The protocol decomposes the task into 2+ SIMPLE subtasks, each proceeding through the full algorithm (GATHER → ... → LEARN). Results are aggregated via AGGREGATION_FLOW.

---

## Agent Flow Architecture

### DECOMPOSE_FLOW

```
┌────────────────────────────────────────────────────┐
│  clarification (conditional) - Clarify scope       │
│       ↓                                            │
│  analysis - Identify decomposition axes            │
│       ↓                                            │
│  synthesis - Generate subtasks JSON                │
│       ↓                                            │
│  validation - GO/NO-GO verdict                     │
└────────────────────────────────────────────────────┘
```

### AGGREGATION_FLOW (after all subtasks complete)

```
┌────────────────────────────────────────────────────┐
│  synthesis - Combine subtask outputs into final    │
└────────────────────────────────────────────────────┘
```

---

## Entry Point

```bash
python3 decompose/entry.py --state <session_id>
```

### With Legacy Mode (no agent flow)

```bash
python3 decompose/entry.py --state <session_id> --no-flow
```

---

## Subtask Routing

After DECOMPOSE_FLOW completes with GO verdict:

1. `complete_decomposition()` creates AlgorithmState for each subtask
2. Subtasks are registered in parent with dependency graph
3. First ready subtask routes to GATHER
4. After each subtask completes LEARN phase:
   - `on_subtask_complete()` checks progress
   - If more ready → route next to GATHER
   - If all done → `trigger_aggregation()`

---

## Directory Structure

```
decompose/
├── CLAUDE.md           # This file
├── __init__.py         # Package exports
├── entry.py            # Entry point (triggers DECOMPOSE_FLOW)
├── flows.py            # DECOMPOSE_FLOW, AGGREGATION_FLOW definitions
├── complete.py         # Subtask creation and routing handlers
└── content/
    ├── decompose/
    │   ├── clarification.md
    │   ├── analysis.md
    │   ├── synthesis.md
    │   └── validation.md
    └── aggregation/
        └── synthesis.md
```

---

## Flow Definitions (flows.py)

| Flow | Flow ID | Agents |
|------|---------|--------|
| `DECOMPOSE_FLOW` | `decompose-protocol` | clarification → analysis → synthesis → validation |
| `AGGREGATION_FLOW` | `decompose-aggregation` | synthesis |

---

## Completion Handler (complete.py)

| Function | Purpose |
|----------|---------|
| `complete_decomposition(parent, subtasks)` | Create subtask states, route first to GATHER |
| `on_subtask_complete(state)` | Handle subtask completion, route next or aggregate |
| `trigger_aggregation(parent)` | Start AGGREGATION_FLOW |

---

## Subtask JSON Format

From synthesis agent:

```json
[
  {
    "subtask_id": "ST-001",
    "description": "Clear, actionable description",
    "complexity": "simple",
    "dependencies": [],
    "verification_criteria": ["Testable criterion"],
    "context": { "from_parent": "..." }
  }
]
```

---

## Integration with The Last Algorithm

```
entry.py (complexity analysis)
    │
    ├── trivial → DA direct execution
    │
    ├── simple/moderate → GATHER phase (The Last Algorithm)
    │
    └── complex/very_complex → DECOMPOSE protocol
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
                 DECOMPOSE_FLOW          After subtasks:
                 (4 agents)              AGGREGATION_FLOW
                        │
                        ▼
                 Subtask States
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Subtask 1     Subtask 2     Subtask 3
      (SIMPLE)      (SIMPLE)      (SIMPLE)
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
                   Each subtask:
            GATHER → IDEAL → OBSERVE → ...
                → VERIFY → LEARN
```

---

## Critical Constraints

1. **ALL subtasks MUST be SIMPLE** - Enforced by synthesis agent
2. **Valid DAG** - No circular dependencies
3. **State saved before directive** - Critical invariant
4. **Subtasks route to GATHER** - Full algorithm treatment

---

## Tests

Located at: `tests/unit/orchestration/decompose/`

- `test_flows.py` - Flow definition tests
- `test_complete.py` - Completion handler tests
- `test_entry.py` - Entry point tests

Run tests:

```bash
cd .claude/orchestration
source .venv/bin/activate
pytest tests/unit/orchestration/decompose/ -v
```

---

*Last updated: 2026-01-31*
