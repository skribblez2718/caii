# Decompose Protocol

Breaks complex/very_complex tasks into smaller subtasks.

## Status: STUB (Not Yet Implemented)

This protocol is a placeholder. Full implementation is planned for a future session.

---

## Purpose

When a task is classified as `complex` or `very_complex` by the complexity analysis, it routes here instead of directly to GATHER. The goal is to decompose the task into 2+ smaller subtasks, each with complexity <= moderate.

## Expected Behavior

1. Receive task with complexity = complex or very_complex
2. Analyze task to identify natural decomposition points
3. Output 2+ subtasks, each targeting complexity <= moderate
4. Each subtask re-enters complexity analysis
5. Only subtasks <= moderate proceed to GATHER

## Entry Point

```bash
python3 decompose/entry.py --state <session_id>
```

## Integration with The Last Algorithm

```
entry.py (complexity analysis)
    │
    ├── trivial → DA direct execution
    │
    ├── simple/moderate → GATHER phase (The Last Algorithm)
    │
    └── complex/very_complex → DECOMPOSE protocol ← YOU ARE HERE
                                    ↓
                               subtasks re-analyzed
                                    ↓
                               <= moderate → GATHER
```

## Decomposition Strategies (Future)

When implemented, the protocol will consider:

1. **Functional Decomposition** - Split by feature/capability
2. **Component Decomposition** - Split by architectural component
3. **Sequential Decomposition** - Split by phases/stages
4. **Parallel Decomposition** - Split by independent work streams

## Related Files

| File | Purpose |
|------|---------|
| `decompose/entry.py` | Entry point (STUB) |
| `decompose/content/decompose_phase.md` | Phase prompt content (STUB) |
| `state/algorithm_state.py` | State management with complexity field |

---

*Last updated: 2026-01-27*
