---
paths:
  - ".claude/orchestration/inner_loop/**"
---

# Inner Loop - Task Execution

The inner loop handles task execution through 6 phases:

```
OBSERVE (Step 1) → THINK (Step 2) → PLAN (Step 3) → BUILD (Step 4)
                                                         │
                                                         ▼
LEARN (Step 8b) ← VERIFY ← EXECUTE (Step 5) ← [Agents]
```

## Phase Directory Structure

| Directory | Step | Purpose |
|-----------|------|---------|
| `observe/` | 1 | Semantic understanding of task |
| `think/` | 2 | Chain of thought reasoning |
| `plan/` | 3 | Tree of thought planning |
| `build/` | 4 | Agent orchestration |
| `execute/` | 5 | Task execution |
| `learn/` | 8b | Learning capture |

## Phase Entry Point Pattern

Each phase has:
- `entry.py` - Phase entry point
- `content/{phase}_phase.md` - Phase content/instructions

Standard entry point structure:

```python
from orchestration.entry_base import PhaseConfig, run_phase_entry

if __name__ == "__main__":
    run_phase_entry(
        __file__,
        PhaseConfig(
            step_num=1,
            phase_name="OBSERVE",
            content_file="observe_phase.md",
            description="OBSERVE Phase (Step 1)",
        ),
    )
```

## Bootstrap Pattern (Required)

Entry points need path setup for orchestration imports:

```python
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p
```

## Phase Transitions

Phases transition via FSM with validation:

```python
from orchestration.state.algorithm_fsm import AlgorithmFSM, AlgorithmPhase

fsm = AlgorithmFSM()
fsm.transition(AlgorithmPhase.OBSERVE)  # Must follow valid transition
```

## State Management

- Session ID passed via `--state` argument
- State files in `.claude/orchestration/state/sessions/`
- Always save state BEFORE printing directive

## Flow Phase Modes

| Mode | Description |
|------|-------------|
| **Legacy** | Loads static content from `content_file` |
| **Agent Flow** | Invokes agent chain via `flow_invoker.py` |

Use agent flow mode for phases requiring cognitive agent orchestration.
