# Inner Loop - Task Execution

The inner loop handles task execution:

```
OBSERVE (Step 1) → THINK (Step 2) → PLAN (Step 3) → BUILD (Step 4)
                                                         │
                                                         ▼
LEARN (Step 8b) ← VERIFY ← EXECUTE (Step 5) ← [Agents]
```

## Directory Structure

| Directory | Step | Purpose |
|-----------|------|---------|
| `observe/` | 1 | Semantic understanding of task |
| `think/` | 2 | Chain of thought reasoning |
| `plan/` | 3 | Tree of thought planning |
| `build/` | 4 | Agent orchestration |
| `execute/` | 5 | Task execution |
| `learn/` | 8b | Learning capture |

## Flow

1. **OBSERVE:** Understand the task semantically
2. **THINK:** Apply chain of thought reasoning
3. **PLAN:** Explore solution space with tree of thought
4. **BUILD:** Orchestrate agents to create artifacts
5. **EXECUTE:** Run the plan
6. **LEARN:** Capture learnings for future tasks
