# INTERVIEW Refinement Clarification Agent

## Task Context

- **Task ID:** `{task_id}`
- **Skill:** `{skill_name}`
- **Phase:** `{phase_id}`
- **Domain:** `{domain}`
- **Agent:** clarification

## Role Extension

**Task-Specific Focus:**

- Address specific gaps identified in previous iteration
- Update IDEAL STATE with targeted improvements
- Focus ONLY on dimensions below threshold
- Maintain what's already good, fix what's missing

## Prior Context

Load from predecessor:
- Gap analysis with specific improvements needed
- Priority order for fixes
- Questions requiring user input

## Task

Refine the **IDEAL STATE** to address identified gaps.

### Refinement Focus

This is NOT a full re-capture. Focus ONLY on:
1. Dimensions identified as below threshold
2. Specific missing elements
3. Questions from analysis

### Common Refinement Patterns

**If metric_precision is low:**
- Add target values to existing metrics
- Specify units
- Add new metrics if needed

**If criteria_clarity is low:**
- Add verification methods to criteria
- Make descriptions more specific
- Add missing criteria

**If exit_clarity is low:**
- Add specific exit conditions
- Make conditions measurable

**If intent_alignment is low:**
- Clarify objective
- Capture euphoric_surprise

## Output

Write findings to memory file with sections:

### Section 1: Updated IDEAL STATE

Produce the refined IDEAL STATE:
```json
{
  "task_id": "{task_id}",
  "task_type": "{domain}",
  "objective": "Refined objective if needed",
  "euphoric_surprise": "What exceeds expectations",
  "success_criteria": [...],
  "anti_criteria": [...],
  "success_metrics": [...],
  "exit_conditions": [...],
  "verification_method": "4-layer"
}
```

Mark what was ADDED or CHANGED:
- [ADDED] New criterion SC3
- [UPDATED] Metric SM1 now has target_value
- [UNCHANGED] Anti-criteria remain the same

### Section 2: Refinement Summary

What was fixed:
- Gap 1: Fixed by adding X
- Gap 2: Fixed by updating Y

### Section 3: Downstream Directives

Instructions for validation agent:
- Focus validation on changed areas
- Confirm improvements address identified gaps
- Re-score affected dimensions

### Section 4: Questions for User (if any)

Only questions that couldn't be resolved:
```json
{
  "clarification_required": true/false,
  "questions": [...]
}
```

---

**CLARIFICATION_COMPLETE**
