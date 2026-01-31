# DECOMPOSE: Validation

## Context

Verify decomposition quality and provide GO/NO-GO verdict.
This is the final gate before subtask creation and routing.

---

## Validation Checklist

### 1. Complexity Check
- [ ] ALL subtasks are SIMPLE complexity
- [ ] No subtask requires further decomposition
- [ ] Each subtask has focused scope

### 2. Coverage Check
- [ ] Subtasks cover full parent task scope
- [ ] No functionality gaps
- [ ] No significant overlaps

### 3. Dependency Graph Check
- [ ] Valid DAG (no cycles)
- [ ] All dependency IDs exist
- [ ] At least one entry point (no dependencies)
- [ ] Terminal subtasks identified

### 4. Verification Criteria Check
- [ ] All subtasks have verification criteria
- [ ] Criteria are specific and testable
- [ ] No vague or unmeasurable criteria

### 5. Context Check
- [ ] Each subtask has sufficient context
- [ ] Parent task context preserved
- [ ] Handoff information clear

---

## Verdict Format

Provide verdict in this format:

### GO Verdict
```
**VERDICT: GO**

Decomposition passes all validation checks.
Ready to create subtask states and route to GATHER.

Summary:
- Subtask count: N
- Entry points: [list]
- Terminal subtasks: [list]
- Estimated parallel capacity: N
```

### NO-GO Verdict
```
**VERDICT: NO-GO**

Decomposition fails validation. Issues found:

1. [Issue description]
   - Impact: [what breaks]
   - Remediation: [how to fix]

2. [Issue description]
   - Impact: [what breaks]
   - Remediation: [how to fix]

Required actions before re-validation:
- [ ] Action 1
- [ ] Action 2
```

---

## Output Focus

1. Run through ALL checklist items
2. Note any failures with details
3. Provide clear GO or NO-GO verdict
4. If NO-GO, provide actionable remediation steps
