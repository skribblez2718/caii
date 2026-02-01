# Outer Loop - The Last Algorithm

The outer loop handles meta-level task management: requirements gathering, success criteria definition, and verification.

```
GATHER → INTERVIEW → [Inner Loop] → VERIFY
   │          │                        │
   │          │                        │
   ▼          ▼                        ▼
Johari    Success Criteria     Verification Against
Window    Anti-Criteria        IDEAL STATE
Discovery Metrics
```

## Directory Structure

| Directory | Phase | Purpose |
|-----------|-------|---------|
| `gather/` | GATHER | Johari Window Discovery - eliminate ambiguity |
| `interview/` | INTERVIEW | Capture success criteria, anti-criteria, metrics |
| `ideal_state/` | INTERVIEW | Legacy alias for interview |
| `verify/` | VERIFY | Verify output against IDEAL STATE |

## Phase Details

### GATHER Phase

**Purpose:** Apply the Johari Window Protocol to surface unknowns and clarify requirements.

**Key Operations:**
1. Classify task domain (CODING, RESEARCH, etc.)
2. Trigger research → analysis agent flow
3. Surface blind spots and hidden assumptions
4. Produce clarified requirements

**Entry Point:** `gather/entry.py --state <session_id>`

**Agent Flow:** `GATHER_FLOW` (research → analysis)

### INTERVIEW Phase (IDEAL STATE)

**Purpose:** Define verifiable success criteria before execution begins.

**Captures:**
- **Success Criteria:** What MUST be true (must-have, should-have, nice-to-have)
- **Anti-Criteria:** What MUST NOT happen
- **Metrics:** Quantifiable measures of success
- **Exit Condition:** Definition of done

**Completeness Threshold:** 95% before proceeding to inner loop.

**Entry Point:** `interview/entry.py --state <session_id>` or `ideal_state/entry.py --state <session_id>`

### VERIFY Phase

**Purpose:** Validate output against IDEAL STATE using 4-layer verification.

**Verification Layers:**
1. **Objective (50%):** Automated checks (tests, linting, build)
2. **Heuristic (30%):** Pattern-based rules (complexity, style)
3. **Semantic (20%):** LLM-judged quality alignment
4. **User Confirmation:** Ground truth for critical decisions

**Outcomes:**
| Status | Score | Action |
|--------|-------|--------|
| VERIFIED | ≥ 0.9 | Proceed to LEARN |
| GAPS_IDENTIFIED | 0.6-0.9 | Loop back to INNER_LOOP (max 3) |
| CRITICAL_FAILURE | < 0.6 | Escalate to user |

**Entry Point:** `verify/entry.py --state <session_id>`

**Agent Flow:** `VERIFY_FLOW`

## FSM Transitions

```
INITIALIZED → GATHER → INTERVIEW → INNER_LOOP → VERIFY
                                                   │
                                      ┌────────────┤
                                      │            │
                                      ▼            ▼
                               INNER_LOOP       LEARN → COMPLETED
                              (loop back)
```

Maximum loop-back iterations: 3

## Flow Integration

From VERIFY, the system can:
1. **PROCEED** to LEARN phase (all criteria met)
2. **LOOP_BACK** to INNER_LOOP (gaps identified, iterations remaining)
3. **ESCALATE** to user (critical failure or max iterations reached)

---
*See `gather/CLAUDE.md`, `interview/CLAUDE.md`, and `verify/CLAUDE.md` for phase-specific details.*
