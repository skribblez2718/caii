# The Last Algorithm - System Architecture

Multi-agent orchestration system for Claude Code implementing cognitive workflows.

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER QUERY                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPLEXITY ANALYSIS (entry.py)                         │
│   Classifies task: TRIVIAL | SIMPLE | MODERATE | COMPLEX | VERY_COMPLEX     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
     ┌──────────────┐      ┌────────────────┐      ┌────────────────────────┐
     │   TRIVIAL    │      │ SIMPLE/MODERATE │      │  COMPLEX/VERY_COMPLEX  │
     │  DA Direct   │      │                │      │                        │
     │  (no state)  │      │                │      │                        │
     └──────────────┘      │                │      │                        │
                           ▼                │      ▼                        │
                    ┌──────────────┐        │   ┌──────────────────────┐   │
                    │ Create State │        │   │   DECOMPOSE PROTOCOL │   │
                    │ AlgorithmState│       │   │                      │   │
                    └──────────────┘        │   │ clarification        │   │
                           │                │   │      ↓               │   │
                           │                │   │ analysis             │   │
                           │                │   │      ↓               │   │
                           ▼                │   │ synthesis            │   │
                                            │   │      ↓               │   │
     ╔════════════════════════════════╗     │   │ validation (GO/NO-GO)│   │
     ║     OUTER LOOP                 ║     │   └──────────┬───────────┘   │
     ║                                ║     │              │               │
     ║  ┌────────────────────────┐    ║     │              ▼               │
     ║  │ GATHER (Step 0)        │    ║     │    ┌─────────────────────┐   │
     ║  │ Johari Window Protocol │    ║     │    │  Subtask Creation   │   │
     ║  │ Clarify requirements   │    ║     │    │  (all SIMPLE)       │   │
     ║  └───────────┬────────────┘    ║     │    └─────────────────────┘   │
     ║              │                 ║     │              │               │
     ║              ▼                 ║     │    ┌─────────┼─────────┐     │
     ║  ┌────────────────────────┐    ║     │    ▼         ▼         ▼     │
     ║  │ IDEAL STATE (Step 0.5) │    ║     │ Subtask1  Subtask2  Subtask3 │
     ║  │ Success criteria       │    ║     │    │         │         │     │
     ║  │ Anti-criteria          │    ║◄────┼────┴─────────┴─────────┘     │
     ║  └───────────┬────────────┘    ║     │    Each routes to GATHER     │
     ║              │                 ║     │                              │
     ╚══════════════╪═════════════════╝     │                              │
                    │                        │                              │
     ╔══════════════╪═════════════════╗     │                              │
     ║     INNER LOOP                 ║     │                              │
     ║              │                 ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ OBSERVE (Step 1)       │    ║     │                              │
     ║  │ Semantic understanding │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ THINK (Step 2)         │    ║     │                              │
     ║  │ Chain of thought       │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ PLAN (Step 3)          │    ║     │                              │
     ║  │ Tree of thought        │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ BUILD (Step 4)         │    ║     │                              │
     ║  │ Agent orchestration    │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ EXECUTE (Step 5)       │    ║     │                              │
     ║  │ Run the plan           │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              │                 ║     │                              │
     ╚══════════════╪═════════════════╝     │                              │
                    │                        │                              │
     ╔══════════════╪═════════════════╗     │                              │
     ║     VERIFICATION               ║     │                              │
     ║              │                 ║     │                              │
     ║              ▼                 ║     │                              │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ VERIFY (Step 8)        │    ║     │                              │
     ║  │ Check vs IDEAL STATE   │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              │                 ║     │                              │
     ║       ┌──────┴──────┐          ║     │                              │
     ║       │             │          ║     │                              │
     ║      PASS          FAIL        ║     │                              │
     ║       │             │          ║     │                              │
     ║       ▼             └──────────╬─────┼───► Loop back to OBSERVE     │
     ║  ┌────────────────────────┐    ║     │                              │
     ║  │ LEARN (Step 8.5)       │    ║     │                              │
     ║  │ Extract learnings      │    ║     │                              │
     ║  └───────────┬────────────┘    ║     │                              │
     ║              │                 ║     │                              │
     ╚══════════════╪═════════════════╝     │                              │
                    │                        │                              │
                    ▼                        │                              │
            ┌───────────────┐                │   ┌──────────────────────┐   │
            │   COMPLETED   │                │   │  All subtasks done?  │   │
            └───────────────┘                │   └──────────┬───────────┘   │
                                             │              │               │
                                             │              ▼               │
                                             │   ┌──────────────────────┐   │
                                             │   │  AGGREGATION FLOW    │   │
                                             │   │  synthesis agent     │   │
                                             │   │  combines results    │   │
                                             │   └──────────────────────┘   │
                                             │              │               │
                                             │              ▼               │
                                             │      ┌───────────────┐       │
                                             │      │   COMPLETED   │       │
                                             │      └───────────────┘       │
                                             └──────────────────────────────┘
```

## Complexity Categories (METR Scale)

| Category | Routing | State Created |
|----------|---------|---------------|
| **TRIVIAL** | DA Direct Execution | No |
| **SIMPLE** | GATHER → Inner Loop → VERIFY | Yes |
| **MODERATE** | GATHER → Inner Loop → VERIFY | Yes |
| **COMPLEX** | DECOMPOSE → Subtasks → GATHER each | Yes |
| **VERY COMPLEX** | DECOMPOSE (required) → Subtasks → GATHER each | Yes |

### Complexity Classification Criteria

The complexity classifier (`entry.py`) evaluates tasks against the following METR-aligned criteria:

| Category | Criteria | Examples |
|----------|----------|----------|
| **TRIVIAL** | Single-step, obvious answer, no research needed | "What time is it?", "Convert 5 miles to km", Simple greetings |
| **SIMPLE** | 2-5 steps, clear path, minimal research | "Write a function to reverse a string", "Explain X concept" |
| **MODERATE** | Multi-step, requires planning, some ambiguity | "Build a REST API endpoint with validation", "Refactor this code" |
| **COMPLEX** | Multi-component, significant ambiguity, integration | "Add authentication to the application", "Implement feature X" |
| **VERY_COMPLEX** | System-level, architectural decisions, high risk | "Redesign the database schema", "Migrate to microservices" |

**Classification factors:**
- Number of affected files/components
- Degree of ambiguity in requirements
- Integration complexity
- Risk of unintended side effects
- Need for user clarification

## Loop Descriptions

### Outer Loop (GATHER → INTERVIEW)

The outer loop handles requirement gathering and success criteria definition:

- **GATHER phase**: Applies Johari Window Protocol to clarify requirements
- **INTERVIEW phase**: Defines success criteria and anti-criteria (captures IDEAL STATE)

### Inner Loop (OBSERVE → EXECUTE)

The inner loop executes the cognitive workflow:

| Phase | Description |
|-------|-------------|
| **OBSERVE** | Semantic understanding of the task |
| **THINK** | Chain-of-thought reasoning |
| **PLAN** | Tree-of-thought planning |
| **BUILD** | Agent orchestration |
| **EXECUTE** | Run the plan |

### Verification (VERIFY → LEARN)

- **VERIFY phase**: Check results against IDEAL STATE (captured in INTERVIEW)
- **LEARN phase**: Extract learnings for future tasks

## Decompose Protocol

For COMPLEX and VERY_COMPLEX tasks, the decompose protocol breaks work into SIMPLE subtasks:

1. **Clarification** - Gather missing context
2. **Analysis** - Analyze complexity and dependencies
3. **Synthesis** - Create subtask specifications
4. **Validation** - GO/NO-GO decision on decomposition

---
*See `.claude/orchestration/CLAUDE.md` for implementation details.*
