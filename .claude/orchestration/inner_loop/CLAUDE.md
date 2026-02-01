# Inner Loop - Task Execution

The inner loop handles cognitive task execution through a structured workflow.

```
OBSERVE → THINK → PLAN → BUILD → EXECUTE
   │        │       │       │        │
   ▼        ▼       ▼       ▼        ▼
Semantic  Chain   Tree   Agent    Run
Under-    of      of     Orches-  the
standing  Thought Thought tration  Plan
```

## Directory Structure

| Directory | Phase | Purpose |
|-----------|-------|---------|
| `observe/` | OBSERVE | Semantic understanding of task |
| `think/` | THINK | Chain of thought reasoning |
| `plan/` | PLAN | Tree of thought planning |
| `build/` | BUILD | Agent orchestration |
| `execute/` | EXECUTE | Task execution |
| `learn/` | LEARN | Learning capture (after VERIFY) |

## Phase Details

### OBSERVE Phase

**Purpose:** Semantic understanding of the task before reasoning begins.

**Actions:**
1. Parse user intent
2. Identify entities (components, systems, concepts)
3. Map relationships between entities
4. Surface constraints and requirements

**Output:** Semantic model feeding into THINK phase.

**Entry Point:** `observe/entry.py --state <session_id>`

### THINK Phase

**Purpose:** Apply chain of thought reasoning to break down the problem.

**Actions:**
1. Decompose problem into sub-problems
2. Identify dependencies between sub-problems
3. Consider multiple approaches
4. Evaluate trade-offs

**Output:** Reasoned analysis feeding into PLAN phase.

**Entry Point:** `think/entry.py --state <session_id>`

### PLAN Phase

**Purpose:** Explore solution space with tree of thought planning.

**Actions:**
1. Generate multiple solution paths
2. Evaluate paths on feasibility and risk
3. Prune dead-end paths
4. Select optimal approach

**Output:** Concrete plan with ordered steps for BUILD phase.

**Entry Point:** `plan/entry.py --state <session_id>`

### BUILD Phase

**Purpose:** Orchestrate agents to create artifacts.

**Available Agents:**
| Agent | Purpose |
|-------|---------|
| analysis | Decompose problems, identify patterns |
| clarification | Resolve ambiguities with user |
| generation | Create code and artifacts |
| research | Investigate options, gather knowledge |
| synthesis | Integrate findings into recommendations |
| validation | Verify artifacts against criteria |

**Output:** Artifacts ready for EXECUTE phase.

**Entry Point:** `build/entry.py --state <session_id>`

### EXECUTE Phase

**Purpose:** Run the plan and execute the task.

**Guidelines:**
- Follow the plan unless blocked
- Document deviations from plan
- Surface blocking issues immediately
- Capture partial progress

**Output:** Completed work ready for VERIFY phase.

**Entry Point:** `execute/entry.py --state <session_id>`

### LEARN Phase

**Purpose:** Capture learnings for future tasks (runs after VERIFY passes).

**Learning Categories:**
- **Technical:** Code patterns, architecture decisions
- **Process:** Workflow improvements, tool usage
- **Domain:** Business logic, user requirements
- **Meta:** Insights about the learning process itself

**Entry Point:** `learn/entry.py --state <session_id>`

## FSM Transitions

Within the inner loop, phases follow this sequence:

```
OBSERVE → THINK → PLAN → BUILD → EXECUTE → (to VERIFY)
```

Note: The FSM tracks entry into the inner loop as `INNER_LOOP` phase, with individual inner phases tracked conceptually.

## Entry Point Pattern

All inner loop phases use the standard entry point pattern:

```python
from orchestration.entry_base import PhaseConfig, run_phase_entry
from orchestration.state.algorithm_fsm import AlgorithmPhase

if __name__ == "__main__":
    run_phase_entry(
        __file__,
        PhaseConfig(
            phase=AlgorithmPhase.PHASE_NAME,
            phase_name="PHASE_NAME",
            content_file="phase_name.md",
            description="PHASE_NAME Phase",
        ),
    )
```

---
*See individual phase CLAUDE.md files for phase-specific details.*
