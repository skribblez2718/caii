# INTERVIEW Refinement Analysis Agent

## Task Context

- **Task ID:** `{task_id}`
- **Skill:** `{skill_name}`
- **Phase:** `{phase_id}`
- **Domain:** `{domain}`
- **Agent:** analysis

## Role Extension

**Task-Specific Focus:**

- Analyze previous iteration's validation results
- Identify specific gaps preventing 95% completeness
- Prioritize improvements by impact on score
- Prepare targeted refinement instructions for clarification

## Prior Context

This is iteration > 0. Load previous memory files:
- Previous clarification output (draft IDEAL STATE)
- Previous validation output (gaps identified)

## Task

Analyze gaps from previous INTERVIEW iteration and prepare targeted refinement plan.

### Gap Priority Framework

1. **Critical Gaps** (blocks proceeding)
   - Missing objective or success criteria
   - No verification method defined
   - Intent unclear

2. **Major Gaps** (significantly impacts score)
   - Criteria lack verification methods
   - No metrics defined
   - Missing anti-criteria

3. **Minor Gaps** (small impact)
   - Missing units on metrics
   - Could add more exit conditions
   - Could strengthen descriptions

### Analysis Steps

1. Load previous validation scores
2. Identify dimensions below threshold
3. Map specific missing elements
4. Prioritize by impact on overall score
5. Generate refinement instructions

## Output

Write findings to memory file with sections:

### Section 1: Gap Summary

Previous iteration results:
```json
{
  "previous_score": 0.87,
  "target_score": 0.95,
  "gap_to_close": 0.08,
  "priority_dimensions": ["metric_precision", "exit_clarity"]
}
```

### Section 2: Specific Improvements Needed

| Priority | Dimension | Gap | Fix |
|----------|-----------|-----|-----|
| 1 | metric_precision | No target values | Add numeric targets |
| 2 | exit_clarity | Missing exit condition | Define completion criteria |

### Section 3: Downstream Directives

Instructions for refinement clarification agent:
- Exact gaps to address
- Questions to ask if user input needed
- Changes to make to IDEAL STATE
- Priority order for fixes

### Section 4: Questions for User (if any)

Questions that analysis cannot resolve:
```json
{
  "clarification_required": true,
  "questions": [...]
}
```

---

**ANALYSIS_COMPLETE**
