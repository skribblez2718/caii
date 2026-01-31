---
paths:
  - ".claude/orchestration/outer_loop/**"
---

# Outer Loop - The Last Algorithm

The outer loop handles meta-level task management:

```
GATHER (Step 0) → IDEAL STATE (Step 0.5) → [Inner Loop] → VERIFY (Step 8)
     │                    │                                    │
     ▼                    ▼                                    ▼
  Johari           Success Criteria            Verification Against
  Window           Anti-Criteria               IDEAL STATE
  Discovery        Metrics
```

## Phase Directory Structure

| Directory | Step | Purpose |
|-----------|------|---------|
| `gather/` | 0 | Johari Window Discovery - eliminate ambiguity |
| `ideal_state/` | 0.5 | Capture success criteria, anti-criteria, metrics |
| `verify/` | 8 | Verify output against IDEAL STATE |

## GATHER Phase (Step 0)

**Purpose:** Execute Johari Window protocol to surface unknowns and clarify requirements.

**Key Files:**
- `gather/entry.py` - Phase entry
- `gather/content/gather_phase.md` - Johari instructions
- `../johari/protocol.md` - Full Johari framework

**Output:** Clarified requirements with Open/Blind/Hidden/Unknown mapped.

## IDEAL STATE Phase (Step 0.5)

**Purpose:** Define verifiable success criteria before execution.

**Captures:**
- Success criteria (what MUST be true)
- Anti-criteria (what must NOT happen)
- Measurable metrics

**Critical:** IDEAL STATE must be verifiable - no vague success definitions.

## VERIFY Phase (Step 8)

**Purpose:** Validate output against IDEAL STATE criteria.

**Process:**
1. Load IDEAL STATE criteria
2. Check each criterion against actual output
3. Report pass/fail with specific findings
4. If failed: Determine if Inner Loop should re-execute

## Flow Integration

```
Complexity Analysis
        │
        ├── TRIVIAL → DA Direct (no outer loop)
        │
        ├── SIMPLE/MODERATE → GATHER → IDEAL → Inner Loop → VERIFY
        │
        └── COMPLEX/VERY_COMPLEX → DECOMPOSE → subtasks → GATHER
```

## State Transitions

| Transition | Condition |
|------------|-----------|
| GATHER → IDEAL | Requirements clarified |
| IDEAL → OBSERVE (Inner) | Criteria captured |
| LEARN → VERIFY | Inner loop complete |
| VERIFY → Complete | All criteria pass |
| VERIFY → OBSERVE | Re-execution needed |

## Johari Window Protocol

| Quadrant | Description |
|----------|-------------|
| **Open** | Known to both user and system |
| **Blind** | Known to user, unknown to system |
| **Hidden** | Known to system, unknown to user |
| **Unknown** | Unknown to both - must be discovered |

Goal: Convert all quadrants to OPEN before proceeding.
