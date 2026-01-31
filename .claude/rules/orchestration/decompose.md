---
paths:
  - ".claude/orchestration/decompose/**"
---

# DECOMPOSE Protocol

Breaks complex/very_complex tasks into SIMPLE subtasks using agent orchestration.

## Protocol Overview

```
complex/very_complex task
         │
         ▼
┌─────────────────────────────────┐
│       DECOMPOSE_FLOW            │
│  clarification → analysis →     │
│  synthesis → validation         │
└───────────────┬─────────────────┘
                │
                ▼
     List of SIMPLE subtasks
     + Dependency Graph (DAG)
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
 Subtask1    Subtask2    Subtask3
    │           │           │
    ▼           ▼           ▼
 GATHER → ... → LEARN
    │           │           │
    └───────────┼───────────┘
                │
                ▼
┌─────────────────────────────────┐
│       AGGREGATION_FLOW          │
│  synthesis agent combines       │
└─────────────────────────────────┘
```

## Directory Structure

| File | Purpose |
|------|---------|
| `entry.py` | Entry point (triggers DECOMPOSE_FLOW) |
| `flows.py` | DECOMPOSE_FLOW, AGGREGATION_FLOW definitions |
| `complete.py` | Subtask creation and routing handlers |
| `content/decompose/*.md` | Agent content files for decomposition |
| `content/aggregation/*.md` | Agent content files for aggregation |

## Flow Definitions

| Flow | Flow ID | Agents |
|------|---------|--------|
| `DECOMPOSE_FLOW` | `decompose-protocol` | clarification → analysis → synthesis → validation |
| `AGGREGATION_FLOW` | `decompose-aggregation` | synthesis |

## Completion Handlers (complete.py)

| Function | Purpose |
|----------|---------|
| `complete_decomposition(parent, subtasks)` | Create subtask states, route first to GATHER |
| `on_subtask_complete(state)` | Handle subtask completion, route next or aggregate |
| `trigger_aggregation(parent)` | Start AGGREGATION_FLOW |

## Critical Constraints

1. **ALL subtasks MUST be SIMPLE** - Enforced by synthesis agent
2. **Valid DAG** - No circular dependencies in subtask graph
3. **State saved before directive** - Critical invariant
4. **Subtasks route to GATHER** - Full algorithm treatment

## Subtask JSON Format

Output from synthesis agent:

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

## Entry Point Usage

```bash
# Standard mode (triggers agent flow)
python3 decompose/entry.py --state <session_id>

# Legacy mode (no agent flow)
python3 decompose/entry.py --state <session_id> --no-flow
```

## Tests

Located at: `tests/unit/orchestration/decompose/`

- `test_flows.py` - Flow definition tests
- `test_complete.py` - Completion handler tests
- `test_entry.py` - Entry point tests
