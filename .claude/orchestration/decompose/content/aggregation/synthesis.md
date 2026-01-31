# AGGREGATION: Synthesis

## Context

Combine completed subtask outputs into a unified deliverable for the parent task.
All subtasks have completed their full algorithm cycle (GATHER → LEARN).

---

## Aggregation Process

### 1. Load Subtask Outputs

Load memory files from all completed subtasks:
- `.claude/memory/{subtask_id}-*-memory.md`

Extract key outputs from each subtask's LEARN phase.

### 2. Identify Integration Points

Map how subtask outputs connect:
- Dependencies between outputs
- Shared interfaces
- Handoff points
- Data flow

### 3. Resolve Conflicts

If subtask outputs conflict:
- Identify the conflict
- Determine resolution strategy
- Document the resolution

### 4. Synthesize Final Output

Combine subtask outputs into unified deliverable:
- Integrate code changes (if applicable)
- Merge documentation
- Consolidate learnings
- Create unified summary

---

## Output Format

```markdown
## Aggregation Summary

### Subtasks Completed
- ST-001: [brief description of output]
- ST-002: [brief description of output]
- ...

### Integration Points
- [How outputs connect]

### Conflicts Resolved
- [Any conflicts and resolutions, or "None"]

### Final Deliverable
[Unified output for parent task]

### Consolidated Learnings
- [Learning 1]
- [Learning 2]
- ...

### Verification Against Parent Task
- [ ] Original success criteria met
- [ ] All parent task objectives addressed
- [ ] Quality standards maintained
```

---

## Output Focus

Produce a unified deliverable that:
1. Addresses the original parent task fully
2. Integrates all subtask contributions
3. Maintains consistency across pieces
4. Documents any learnings for future reference
