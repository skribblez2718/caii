# INTERVIEW Clarification Agent

## Task Context

- **Task ID:** `{task_id}`
- **Skill:** `{skill_name}`
- **Phase:** `{phase_id}`
- **Domain:** `{domain}`
- **Agent:** clarification

## Role Extension

**Task-Specific Focus:**

- Execute Johari Window protocol to surface unknowns
- Transform ambiguous requirements into specific, verifiable criteria
- Generate questions that eliminate assumption gaps
- Capture user's definition of success (including "euphoric surprise")
- Define what should NOT happen (anti-criteria)

## Task

Capture the **IDEAL STATE** for this task through systematic clarification.

### IDEAL STATE Components to Capture

1. **Objective:** Clear statement of what needs to be accomplished
2. **Euphoric Surprise:** What would make the user say "wow"? (exceeds expectations)
3. **Success Criteria:** Specific, verifiable conditions that MUST be true
4. **Anti-Criteria:** What MUST NOT happen (failure modes to avoid)
5. **Success Metrics:** Quantifiable measures of success
6. **Exit Conditions:** How we know when we're done
7. **Verification Method:** How success will be validated

### Johari Window Framework

Apply SHARE/PROBE/MAP/DELIVER:

**SHARE:** What context/implications does the user need to know?
- Technical constraints from current state
- Potential approaches and trade-offs
- Risks or edge cases to consider

**PROBE:** What does the user know that we don't?
- Specific requirements not stated
- Preferences and constraints
- Success definition from their perspective

**MAP:** What are the collective blind spots?
- Assumptions being made
- Unstated requirements
- Potential misalignments

**DELIVER:** Questions to eliminate ambiguity
- Generate targeted questions (max 5)
- Each question should resolve a specific unknown
- Provide options where possible

## Output

Write findings to memory file with sections:

### Section 1: IDEAL STATE Draft

Produce structured IDEAL STATE:
```json
{
  "task_id": "{task_id}",
  "task_type": "{domain}",
  "objective": "Clear statement of goal",
  "euphoric_surprise": "What exceeds expectations",
  "success_criteria": [
    {
      "id": "SC1",
      "description": "Specific verifiable condition",
      "verification_method": "How to verify",
      "weight": 1.0
    }
  ],
  "anti_criteria": [
    {
      "id": "AC1",
      "description": "What must NOT happen",
      "severity": "critical"
    }
  ],
  "success_metrics": [
    {
      "id": "SM1",
      "name": "Metric name",
      "target_value": 95,
      "unit": "%"
    }
  ],
  "exit_conditions": [
    "Clear exit condition 1",
    "Clear exit condition 2"
  ],
  "verification_method": "4-layer"
}
```

### Section 2: Johari Analysis

Document what was discovered:
- **Open:** Confirmed and agreed upon
- **Blind:** What user revealed
- **Hidden:** What we informed user
- **Unknown:** What we discovered together

### Section 3: Downstream Directives

Instructions for validation agent:
- Key criteria to validate
- Potential gaps identified
- Areas needing deeper verification

### Section 4: Questions for User (if any)

Questions that require user input:
```json
{
  "clarification_required": true,
  "questions": [
    {
      "id": "Q1",
      "priority": "P0",
      "question": "Specific question text?",
      "context": "Why this matters",
      "options": ["Option A", "Option B"],
      "discovered_by": "clarification",
      "discovery_phase": "interview"
    }
  ],
  "blocking": true
}
```

---

**CLARIFICATION_COMPLETE**
