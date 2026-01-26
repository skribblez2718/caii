# IDEAL STATE CAPTURE

Define explicit success criteria, anti-criteria, and verification methods using "The Last Algorithm" methodology.

**Core Principle:** "Verifiability is the universal ladder" - goals and verification criteria must be identical.

---

## IDEAL STATE Definition Framework

### 1. SUCCESS CRITERIA (What Must Be True)

Define measurable criteria for success. Each criterion must be:
- **Specific:** Clear, unambiguous description
- **Verifiable:** Has a concrete verification method
- **Prioritized:** must-have | should-have | nice-to-have

**Format:**
```
SC-{N}: {Criterion description}
- Verifiable: Yes/No
- Verification Method: {How to verify}
- Priority: must-have | should-have | nice-to-have
```

**Example:**
```
SC-1: User authentication completes within 2 seconds
- Verifiable: Yes
- Verification Method: Performance test measures auth flow duration
- Priority: must-have
```

### 2. ANTI-CRITERIA (What Must Be Avoided)

Define explicit failure conditions - things that MUST NOT happen.

**Format:**
```
AC-{N}: {Anti-criterion description}
- Verifiable: Yes/No
- Verification Method: {How to verify absence}
```

**Example:**
```
AC-1: Plaintext passwords must never be stored or transmitted
- Verifiable: Yes
- Verification Method: Security scan detects no plaintext password storage
```

### 3. SUCCESS METRICS (Quantifiable Measures)

Define measurable metrics for evaluating success.

**Format:**
```
SM-{N}: {Metric name}
- Target Value: {Specific target or range}
- Measurement Method: {How to measure}
```

**Example:**
```
SM-1: API response time
- Target Value: < 100ms p95
- Measurement Method: Load test with 1000 concurrent requests
```

### 4. EXIT CONDITION (When Is It Done?)

Define the precise condition that indicates task completion.

**Example:**
```
EXIT CONDITION: All must-have success criteria verified AND
no anti-criteria violated AND all success metrics within target ranges
```

---

## Sufficiency Assessment

After defining the IDEAL STATE, assess its completeness:

### Completeness Checklist

| Dimension | Question | Weight |
|-----------|----------|--------|
| **Intent Clarity** | Is the user's goal unambiguously defined? | 25% |
| **Scope Boundaries** | Are in-scope and out-of-scope items explicit? | 20% |
| **Verification Coverage** | Can every criterion be objectively verified? | 25% |
| **Anti-Criteria Coverage** | Are failure modes and constraints captured? | 15% |
| **Metrics Completeness** | Are success metrics quantifiable? | 15% |

### Completeness Score Calculation

```
Score = (Intent_Clarity * 0.25) + (Scope_Boundaries * 0.20) +
        (Verification_Coverage * 0.25) + (Anti_Criteria_Coverage * 0.15) +
        (Metrics_Completeness * 0.15)
```

Rate each dimension 0.0 to 1.0, then calculate weighted average.

### Exit Conditions for Step 0.5

1. **PROCEED to Step 1** when:
   - Completeness Score >= 95%, OR
   - Max iterations (5) reached

2. **ITERATE** (loop back to Step 0.5) when:
   - Completeness Score < 95% AND
   - Iterations < 5 AND
   - User clarification obtained

3. **HALT for Clarification** when:
   - Critical gaps exist that cannot be inferred
   - User input is required to proceed

---

## Output Requirements

After processing this step, produce:

### IDEAL STATE Document

```markdown
## IDEAL STATE v{iteration}

### Success Criteria
{List all SC-N items}

### Anti-Criteria
{List all AC-N items}

### Success Metrics
{List all SM-N items}

### Exit Condition
{Define when task is complete}

### Sufficiency Assessment
- Intent Clarity: {score}/1.0
- Scope Boundaries: {score}/1.0
- Verification Coverage: {score}/1.0
- Anti-Criteria Coverage: {score}/1.0
- Metrics Completeness: {score}/1.0
- **Completeness Score: {weighted_score}%**

### Gaps (if any)
{List remaining uncertainties or missing information}
```

### Decision

Based on completeness score:

- **>= 95%:** State "IDEAL STATE sufficient - proceeding to Step 1"
- **< 95% with gaps:** Use AskUserQuestion to gather missing information, then iterate
- **< 95% but inferable:** Iterate with refined criteria based on reasonable assumptions

---

## CRITICAL RULE: Dynamic Clarification

This step supports **0-5 clarification cycles** based on need:

- **Simple tasks:** May achieve 95% in cycle 1 (no extra iterations needed)
- **Complex tasks:** May need 3-5 cycles to fully specify
- **No mandatory cycles:** Exit immediately when sufficient

**Key Insight:** Over-reasoning degrades performance. Exit as soon as IDEAL STATE is clear enough to verify success.

---

## AskUserQuestion Integration

When completeness < 95% and critical gaps exist, invoke AskUserQuestion:

```
AskUserQuestion tool parameters:
{
  "questions": [
    {
      "question": "What specific outcome would make this task successful?",
      "header": "Success Vision",
      "options": [
        {"label": "Option A", "description": "Description"},
        {"label": "Option B", "description": "Description"}
      ],
      "multiSelect": false
    }
  ]
}
```

**Focus areas by iteration:**
- **Cycle 1:** Intent, success vision, domain classification
- **Cycle 2:** Scope boundaries, component identification, constraints
- **Cycle 3:** Technical requirements, measurable criteria, edge cases
- **Cycles 4-5:** Anti-criteria, verification methods, assumption validation
