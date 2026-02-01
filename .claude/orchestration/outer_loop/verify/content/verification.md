# VERIFY Phase

**Task ID:** {task_id}

---

## Purpose

Verify output against IDEAL STATE using 4-layer verification.

## 4-Layer Verification Protocol

### Layer 1: Objective (50% weight)

**Automatable checks:**
- [ ] All tests pass?
- [ ] Syntax/linting clean?
- [ ] Format requirements met?
- [ ] Build successful?

### Layer 2: Heuristic (30% weight)

**Pattern-based rules:**
- [ ] Code complexity within limits?
- [ ] Style guide compliance?
- [ ] Design pattern adherence?
- [ ] No obvious anti-patterns?

### Layer 3: Semantic (20% weight)

**LLM-judged quality:**
- [ ] Intent alignment with objective?
- [ ] Reasoning clarity?
- [ ] Implementation matches specification?

### Layer 4: User Confirmation (Final)

**Ground truth verification:**
- [ ] User review requested for critical decisions?
- [ ] Assumptions validated?
- [ ] Edge cases considered?

---

## Anti-Criteria Check (CRITICAL)

**Any violation = CRITICAL_FAILURE:**
- [ ] No forbidden behaviors present?
- [ ] No security vulnerabilities introduced?
- [ ] No data integrity issues?
- [ ] Scope boundaries maintained?

---

## Verification Result

Based on weighted scores:

| Status | Overall Score | Action |
|--------|--------------|--------|
| **VERIFIED** | ≥ 0.9 | Proceed to LEARN phase |
| **GAPS_IDENTIFIED** | 0.6 - 0.9 | Loop back to INNER_LOOP (max 3) |
| **CRITICAL_FAILURE** | < 0.6 or anti-criteria violated | Escalate to user |

---

## Output Requirements

Document in memory file:
1. Layer scores (objective, heuristic, semantic)
2. Overall weighted score
3. Verification status
4. Identified gaps (if any)
5. Recommendations for improvement

**Memory Path:** `.claude/memory/{task_id}-validation-memory.md`
