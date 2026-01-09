# Execution Protocols Documentation

**Purpose:** Reference documentation for the Python-enforced execution protocol system.

---

## Overview

Execution protocols are automatically dispatched by the reasoning protocol after Step 8 routing is validated. The routing_gate.py module validates task triviality before allowing direct execution. The `dispatcher.py` script routes to the appropriate protocol's `entry.py`, which prints directives for the orchestrator to follow.

---

## Protocol Types

| Protocol | Steps | Purpose |
|----------|-------|---------|
| Skill Orchestration | 6 | Multi-phase cognitive workflows matching formal skill patterns |
| Dynamic Skill Sequencing | 5 | Flexible cognitive workflows using orchestrate-* atomic skills |

**Note:** Trivial tasks (single file, ≤5 lines, mechanical operations) are handled via direct tool usage after passing the routing gate validation. This is not a formal protocol but rather a bypass for simple operations.

---

## Architecture

### Routing Gate Module

**Path:** `${CAII_DIRECTORY}/.claude/orchestration/protocols/execution/routing_gate.py`

The routing gate module provides triviality validation to determine if tasks can bypass formal protocols. It implements a self-assessment pattern where the orchestrator evaluates tasks against explicit criteria before routing decisions.

**Core Components:**

- **TrivialCriteria dataclass:** 5 boolean fields representing triviality criteria (single_file, five_lines_or_fewer, mechanical_operation, no_research_required, no_decisions_needed)
- **GateDecision enum:** Routing outcomes (TRIVIAL_APPROVED, AGENT_REQUIRED, CLARIFICATION_NEEDED)
- **RoutingGate class:** Generates self-assessment prompts and parses orchestrator responses to determine routing

**Fail-Secure Design:**

When ANY criterion fails or ambiguity exists, the gate defaults to skill orchestration or dynamic skill sequencing. Direct tool usage requires ALL 5 triviality criteria explicitly satisfied. This ensures cognitive oversight for non-trivial tasks.

### Directory Structure

```
${CAII_DIRECTORY}/.claude/orchestration/protocols/execution/
├── __init__.py            # Package exports
├── CLAUDE.md              # System documentation
│
├── config/                # Configuration module
│   ├── __init__.py
│   └── config.py          # Protocol types, routes, step definitions, helpers
│
├── core/                  # Core execution components
│   ├── __init__.py
│   ├── dispatcher.py      # Route dispatcher (reasoning → execution)
│   ├── routing_gate.py    # Triviality gate for direct tool usage
│   ├── state.py           # ExecutionState class
│   └── fsm.py             # Finite state machines per protocol
│
├── steps/                 # Shared step infrastructure
│   ├── __init__.py
│   └── base.py            # ExecutionBaseStep abstract base class
│
├── skill/                 # 6-step workflow
│   ├── CLAUDE.md
│   ├── entry.py
│   ├── complete.py
│   ├── steps/
│   │   ├── step_1_generate_task_id.py
│   │   ├── step_2_classify_domain.py
│   │   ├── step_3_read_skill.py
│   │   ├── step_4_create_memory.py
│   │   ├── step_5_trigger_agents.py
│   │   └── step_6_complete_workflow.py
│   ├── content/           # Step instructions (step_1.md - step_6.md)
│   └── state/             # Session state files (gitignored)
│
└── dynamic/               # 5-step workflow
    ├── CLAUDE.md
    ├── entry.py
    ├── complete.py
    ├── steps/
    │   ├── step_1_analyze_requirements.py
    │   ├── step_2_plan_sequence.py
    │   ├── step_3_invoke_skills.py
    │   ├── step_4_verify_completion.py
    │   └── step_5_complete.py
    ├── content/           # Step instructions
    └── state/             # Session state files (gitignored)
```

---

## FSM Definitions

### Skill Orchestration (6 steps + 2 terminal states)

```
INITIALIZED → GENERATE_TASK_ID → CLASSIFY_DOMAIN → READ_SKILL →
CREATE_MEMORY → TRIGGER_AGENTS → COMPLETE_WORKFLOW → COMPLETED
```

**When to Use:**
- Task matches a defined composite skill pattern (develop-project, perform-research, etc.)
- Multi-phase cognitive work requiring formal workflow

### Dynamic Skill Sequencing (5 steps + 2 terminal states)

```
INITIALIZED → ANALYZE_REQUIREMENTS → PLAN_SEQUENCE →
INVOKE_SKILLS → VERIFY_COMPLETION → COMPLETE → COMPLETED
```

**When to Use:**
- Task requires multiple cognitive functions but doesn't match existing composite skill
- Novel task patterns requiring flexible orchestration
- The orchestrator determines which orchestrate-* atomic skills to invoke dynamically

**Key Difference from Skill Orchestration:**
- No formal skill definition required
- The orchestrator dynamically determines which orchestrate-* atomic skills to invoke
- More flexible for novel task patterns that don't match existing composite skills

---

## Execution Flow

```
Reasoning Protocol Step 8 completes
              ↓
set_route.py --route <final_route>
              ↓
dispatcher.py (creates ExecutionState, prints directive)
              ↓
entry.py (prints Step 1 directive)
              ↓
step_1_*.py (transitions FSM, prints Step 2 directive)
              ↓
...continues until complete.py...
              ↓
complete.py (final aggregation, learning prompt)
```

---

## Related Files

- `config/config.py` - ProtocolType enum, route mapping, step definitions
- `core/fsm.py` - FSM classes with valid state transitions
- `core/state.py` - ExecutionState class for session persistence
- `core/routing_gate.py` - Triviality validation module
- `core/dispatcher.py` - Route dispatch logic
- `steps/base.py` - Abstract base class for all step scripts

---

## Pythonized Execution Protocols

Execution protocols are fully pythonized in `${CAII_DIRECTORY}/.claude/orchestration/protocols/execution/`:

| Protocol | Location |
|----------|----------|
| Skill Orchestration | `protocols/execution/skill/` |
| Dynamic Skill Sequencing | `protocols/execution/dynamic/` |

Each protocol directory contains:
- `entry.py` - Python entry point
- `content/` - Step markdown files printed to STDOUT
- `steps/` - Individual step Python scripts
- `state/` - Session state files
