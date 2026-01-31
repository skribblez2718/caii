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

## Loop Descriptions

### Outer Loop (Steps 0-0.5)

The outer loop handles requirement gathering and success criteria definition:

- **GATHER (Step 0)**: Applies Johari Window Protocol to clarify requirements
- **IDEAL STATE (Step 0.5)**: Defines success criteria and anti-criteria

### Inner Loop (Steps 1-5)

The inner loop executes the cognitive workflow:

| Step | Name | Description |
|------|------|-------------|
| 1 | OBSERVE | Semantic understanding of the task |
| 2 | THINK | Chain-of-thought reasoning |
| 3 | PLAN | Tree-of-thought planning |
| 4 | BUILD | Agent orchestration |
| 5 | EXECUTE | Run the plan |

### Verification (Step 8+)

- **VERIFY (Step 8)**: Check results against IDEAL STATE
- **LEARN (Step 8.5)**: Extract learnings for future tasks

## Decompose Protocol

For COMPLEX and VERY_COMPLEX tasks, the decompose protocol breaks work into SIMPLE subtasks:

1. **Clarification** - Gather missing context
2. **Analysis** - Analyze complexity and dependencies
3. **Synthesis** - Create subtask specifications
4. **Validation** - GO/NO-GO decision on decomposition

---
*See `.claude/orchestration/CLAUDE.md` for implementation details.*
