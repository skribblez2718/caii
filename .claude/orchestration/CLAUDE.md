# Orchestration System Index

Python-based orchestration implementing The Last Algorithm.

**USAGE:** Reference paths below WITHOUT `@` prefix. Use `Read` tool with `offset`/`limit` to load specific sections when needed.

---

## Quick Reference

| Topic | File | Lines |
|-------|------|-------|
| **This Index** | `.claude/orchestration/CLAUDE.md` | 1-180 |
| **DA Core** | `.claude/DA.md` | 1-503 |

---

## Architecture Overview

```
submit.py (hook)
    │
    ▼
entry.py (5-category complexity analysis)
    │
    ├── trivial → DA direct execution (no state)
    │
    ├── simple/moderate → GATHER phase (The Last Algorithm)
    │                          │
    │                     OUTER LOOP (gather → ideal → verify)
    │                          │
    │                     INNER LOOP (observe → think → plan → build → execute → learn)
    │
    └── complex/very_complex → DECOMPOSE protocol
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
             DECOMPOSE_FLOW                   After subtasks:
             (clarification →                 AGGREGATION_FLOW
              analysis →                      (synthesis)
              synthesis →
              validation)
                    │
                    ▼
             Subtask States (all SIMPLE)
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Subtask 1  Subtask 2  Subtask 3
          │         │         │
          └─────────┼─────────┘
                    │
                    ▼
               Each subtask:
        GATHER → IDEAL → Inner Loop → VERIFY → LEARN
```

**Key Principle:** Python enforces sequence. LLM makes decisions.

### Complexity Categories (METR Scale)

| Category | Routing | State Created |
|----------|---------|---------------|
| **TRIVIAL** | DA Direct Execution | No |
| **SIMPLE** | The Last Algorithm (GATHER) | Yes |
| **MODERATE** | The Last Algorithm (GATHER) | Yes |
| **COMPLEX** | DECOMPOSE Protocol | Yes |
| **VERY COMPLEX** | DECOMPOSE Protocol | Yes |

---

## File Index

### Agents (`.claude/agents/`)

| Agent | File | Lines | Key Sections |
|-------|------|-------|--------------|
| **analysis** | `agents/analysis.md` | 299 | Identity: 9-32, Execution Protocol: 50-78, Output Format: 79-end |
| **clarification** | `agents/clarification.md` | 304 | Identity: 9-44, Pre-Clarification: 46-end |
| **generation** | `agents/generation.md` | 321 | Identity: 9-49, Execution Protocol: 50-78, Output Format: 79-end |
| **memory** | `agents/memory.md` | 251 | Identity: 9-40, Impasse Types: 41-70, Execution Protocol: 71-end |
| **research** | `agents/research.md` | 369 | Identity: 9-84, Execution Protocol: 85-113, Output Format: 114-end |
| **synthesis** | `agents/synthesis.md` | 292 | Identity: 9-49, Execution Protocol: 50-78, Output Format: 79-end |
| **validation** | `agents/validation.md` | 330 | Identity: 9-36, Context Adaptation: 34-end |

### Documentation (`.claude/docs/`)

| Document | File | Lines | Key Sections |
|----------|------|-------|--------------|
| **Agent Protocol** | `docs/agent-protocol-reference.md` | 175 | Validation Checklist: 13-43, Quick Reference: 57-112, Domain Standards: 113-156 |
| **Agent Registry** | `docs/agent-registry.md` | 271 | Agents: 9-142, Cognitive Architecture: 143-end |
| **Code Generation** | `docs/code-generation-reference.md` | 201 | Context by Domain: 17-55, Test Patterns: 68-107, Workflows: 108-end |
| **Cognitive Taxonomy** | `docs/cognitive-function-taxonomy.md` | 438 | (Full file - taxonomy reference) |
| **Context Management** | `docs/context-management.md` | 241 | Loading Patterns: 16-92, Pruning: 93-end |
| **Domain Adaptation** | `docs/domain-adaptation-examples.md` | 413 | Technical: 21-100, Personal: 102-164, Creative: 165-210, Professional: 212-end |
| **Execution Protocols** | `docs/execution-protocols.md` | 165 | Protocol Types: 13-21, FSM Definitions: 75-121 |
| **Johari Reference** | `docs/johari-reference.md` | 474 | Format Matrix: 9-32, Token Limits: 33-55, Compression: 56-113, Types: 106-193 |
| **Philosophy** | `docs/philosophy.md` | 367 | (Full file - system philosophy) |
| **Skill Catalog** | `docs/skill-catalog.md` | 111 | Skill Types: 7-15, Composite: 16-43, Atomic: 44-80, Selection Guide: 81-end |
| **Workflow Validation** | `docs/workflow-validation-guide.md` | 216 | Token Budget: 5-32, Python Requirements: 33-64, Phase Gates: 80-end |

### Orchestration Loop Files

#### Pre-Loop Protocols (`.claude/orchestration/decompose/`)

| Protocol | CLAUDE.md | Key Files | Purpose |
|----------|-----------|-----------|---------|
| **DECOMPOSE** | `decompose/CLAUDE.md` | `flows.py`, `complete.py` | Task decomposition into SIMPLE subtasks |

**DECOMPOSE Protocol Flows:**

| Flow | Flow ID | Agents | Purpose |
|------|---------|--------|---------|
| `DECOMPOSE_FLOW` | `decompose-protocol` | clarification → analysis → synthesis → validation | Break task into subtasks |
| `AGGREGATION_FLOW` | `decompose-aggregation` | synthesis | Combine subtask results |

**Completion Handlers (`complete.py`):**

| Function | Purpose |
|----------|---------|
| `complete_decomposition(parent, subtasks)` | Create subtask states, route first to GATHER |
| `on_subtask_complete(state)` | Handle subtask completion, route next or aggregate |
| `trigger_aggregation(parent)` | Start AGGREGATION_FLOW |

#### Outer Loop (`.claude/orchestration/outer_loop/`)

| Phase | CLAUDE.md | Content File | Purpose |
|-------|-----------|--------------|---------|
| **GATHER (Step 0)** | `outer_loop/gather/CLAUDE.md` (30 lines) | `outer_loop/gather/content/gather_phase.md` | Agentic information gathering |
| **IDEAL (Step 0.5)** | `outer_loop/ideal_state/CLAUDE.md` (20 lines) | `outer_loop/ideal_state/content/ideal_state_capture.md` | Success criteria capture |
| **VERIFY (Step 8)** | `outer_loop/verify/CLAUDE.md` (21 lines) | `outer_loop/verify/content/verification.md` | Validation against ideal state |

#### Inner Loop (`.claude/orchestration/inner_loop/`)

| Phase | CLAUDE.md | Content File | Purpose |
|-------|-----------|--------------|---------|
| **OBSERVE (Step 1)** | `inner_loop/observe/CLAUDE.md` (13 lines) | `inner_loop/observe/content/observe_phase.md` | State observation |
| **THINK (Step 2)** | `inner_loop/think/CLAUDE.md` (13 lines) | `inner_loop/think/content/think_phase.md` | Analysis and reasoning |
| **PLAN (Step 3)** | `inner_loop/plan/CLAUDE.md` (13 lines) | `inner_loop/plan/content/plan_phase.md` | Strategy formulation |
| **BUILD (Step 4)** | `inner_loop/build/CLAUDE.md` (13 lines) | `inner_loop/build/content/build_phase.md` | Artifact creation |
| **EXECUTE (Step 5)** | `inner_loop/execute/CLAUDE.md` (13 lines) | `inner_loop/execute/content/execute_phase.md` | Action execution |
| **LEARN (Step 8b)** | `inner_loop/learn/CLAUDE.md` (13 lines) | `inner_loop/learn/content/learn_phase.md` | Knowledge extraction |

#### Johari Protocol (`.claude/orchestration/johari/`)

| File | Lines | Purpose |
|------|-------|---------|
| `johari/CLAUDE.md` | 27 | Protocol overview |
| `johari/protocol.md` | - | Full Johari framework content |

#### Entry Point Infrastructure (`.claude/orchestration/`)

| File | Purpose |
|------|---------|
| `entry_base.py` | Factory functions for phase entry points (PhaseConfig, run_phase_entry) |
| `flow_invoker.py` | Shared utility for triggering agent flows (invoke_agent_flow) |

**Flow Invocation Pattern:**

`flow_invoker.py` provides THE single entry point for triggering any agent flow. All phase entry points and advance scripts should use this.

```python
from orchestration.flow_invoker import invoke_agent_flow
from orchestration.skills.perform_tdd.flows import TDD_RED_FLOW

directive = invoke_agent_flow(
    flow=TDD_RED_FLOW,
    task_id=state.session_id,
    skill_name="perform-tdd",
    phase_id="red",
    skill_content_dir=CONTENT_DIR,
    task_description="TDD RED phase",
)
print(directive)
```

#### Agent Chain System (`.claude/orchestration/agent_chain/`)

Infrastructure for agent invocation and chaining. Agents pass context via memory files.

| File | Purpose |
|------|---------|
| `agent_chain/CLAUDE.md` | Full documentation for agent chain system |
| `agent_chain/flow.py` | FlowStep, AgentFlow, ContextPattern dataclasses |
| `agent_chain/state.py` | ChainState for tracking execution |
| `agent_chain/memory.py` | MemoryFile class, load_predecessor_context() |
| `agent_chain/invoker.py` | build_agent_invocation_directive() |
| `agent_chain/orchestrator.py` | ChainOrchestrator class |
| `agent_chain/dynamic.py` | create_dynamic_flow() for DA |

**Key Concepts:**

- **FlowStep**: Single step in agent chain (agent_name, context_pattern, predecessors)
- **AgentFlow**: Complete sequence of FlowSteps
- **ChainOrchestrator**: Manages flow execution, generates directives
- **Memory Files**: `.claude/memory/{task_id}-{agent}-memory.md`

**Learnings Injection:**

- First invocation of each agent includes MANDATORY learnings directive
- Tracked via `ChainState.learnings_injected_for`
- Applies to all skills and protocols using `invoke_agent_flow()`
- See `agent_chain/CLAUDE.md` for full documentation

#### Agent Execution Infrastructure (`.claude/orchestration/agents/`)

| File | Purpose |
|------|---------|
| `agents/config.py` | AGENT_REGISTRY with all 7 agents |
| `agents/base.py` | AgentExecutionState dataclass |
| `agents/entry.py` | agent_entry() for agent initialization |
| `agents/complete.py` | agent_complete() with chain continuation |

#### Learnings System (`.claude/learnings/`)

| Directory | Purpose |
|-----------|---------|
| `learnings/{agent}/` | Agent-specific learnings |
| `learnings/{agent}/heuristics.md` | Decision heuristics |
| `learnings/{agent}/anti-patterns.md` | What to avoid |
| `learnings/{agent}/checklists.md` | Verification checklists |

#### State Management (`.claude/orchestration/state/`)

| File | Purpose |
|------|---------|
| `state/CLAUDE.md` | State system documentation |
| `state/config.py` | Paths, versions, session ID generation |
| `state/base.py` | BaseFSM, BaseState (DRY foundation) |
| `state/algorithm_fsm.py` | AlgorithmPhase enum, AlgorithmFSM |
| `state/algorithm_state.py` | AlgorithmState implementation |
| `state/sessions/` | Runtime state files (gitignored) |

**Key Concepts:**

- **Session ID:** 12-character UUID for tracking
- **FSM:** Phase transitions with validation
- **Critical Invariant:** Always save state BEFORE printing directive
- **--state arg:** All phases receive session ID via `--state` argument

### Research Documents (`.claude/research/`)

| Document | Lines | Topic |
|----------|-------|-------|
| `research/caii-last-algorithm-definitive-guide.md` | 2434 | Complete Last Algorithm reference |
| `research/caii-definitive-optimization-guide.md` | 1040 | Token/performance optimization |
| `research/consistency-sampling.md` | 149 | Self-consistency techniques |
| `research/cov.md` | 142 | Chain of Verification |
| `research/critique.md` | 198 | Self-critique patterns |

---

## Python Coding Standards

**Target Version:** Python 3.11+

### Import Rules (MANDATORY)

**ABSOLUTE IMPORTS ONLY** - Never use relative imports.

```python
# CORRECT
from orchestration.outer_loop.gather import entry

# WRONG - FORBIDDEN
from .outer_loop.gather import entry
```

### Entry Point Factory Pattern

Phase entry points use the factory pattern via `entry_base.py` to eliminate duplication.

**Standard Phase Entry Point (use for all phases):**

```python
"""
PHASE Phase Entry Point (Step N)

Description of what the phase does.
"""

import sys
from pathlib import Path

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

from orchestration.entry_base import PhaseConfig, run_phase_entry

# Step number for this phase (preserved for backward compatibility)
STEP_NUM = 1

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

**PhaseConfig Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `step_num` | float | FSM step number (0, 0.5, 1, 2, etc.) |
| `phase_name` | str | Human-readable name (e.g., "OBSERVE") |
| `content_file` | str | Markdown file in content/ directory (legacy mode) |
| `description` | str | Argparse description string |
| `extra_placeholders` | Optional[Callable] | Function(state) -> Dict for additional substitutions |
| `agent_flow` | Optional[AgentFlow] | AgentFlow for phases using agent orchestration |
| `skill_name` | Optional[str] | Skill name for agent flow mode |
| `skill_content_dir` | Optional[Path] | Path to skill's content directory for agent flow |

**Two Modes:**
1. **Legacy mode** (no agent_flow): Loads static content from `content_file`
2. **Agent flow mode** (with agent_flow): Invokes agent chain via `flow_invoker.py`

**Factory Functions in entry_base.py:**

| Function | Purpose |
|----------|---------|
| `load_state_or_exit(session_id)` | Load state or exit with error |
| `start_phase_or_exit(state, step_num, phase_name)` | Transition phase or exit with error |
| `create_phase_parser(description)` | Create standard argparser with --state |
| `run_phase_entry(caller_file, config, argv)` | Complete phase lifecycle orchestration |

### Bootstrap Pattern (Why Required)

Entry points run as standalone scripts (not modules), so they need to add `.claude/` to `sys.path` for `from orchestration.*` imports to work.

| Aspect | Explanation |
|--------|-------------|
| **Problem** | Scripts invoked as `python3 entry.py` only have their own directory in `sys.path` |
| **Solution** | Walk up to find `orchestration/` directory, add its parent (`.claude/`) to path |
| **Robust** | Works regardless of entry point depth (unlike hardcoded `.parent.parent.parent`) |
| **Clean** | Deletes `_p` variable after use to avoid polluting module namespace |

### Required Patterns

| Pattern | Rule |
|---------|------|
| **Type Hints** | All functions MUST have type hints |
| **DRY** | Shared utilities in `utils.py` |
| **Content Separation** | Python in `.py`, prompts in `content/*.md` |
| **stdout** | Print only: directives, errors, state transitions |

### Script Output Rules

Scripts print to stdout which becomes Claude's context. Minimize output.

**PRINT:** MANDATORY directives, errors (stderr preferred), state transitions, actionable instructions

**DO NOT PRINT:** Decorative banners, redundant info, step summaries, tutorial text, option lists

### Content Loading Pattern

```python
from orchestration.utils import load_content, substitute_placeholders

content = load_content(__file__, "phase_name.md")
prompt = substitute_placeholders(content, user_query=query)
print(prompt)
```

---

## How to Use This Index

1. **Find the topic** in tables above
2. **Note the file path and line range** for relevant section
3. **Use Read tool** with offset/limit:
   ```
   Read file_path offset=START limit=LENGTH
   ```

**Example:** To read agent protocol quick reference:
```
Read .claude/docs/agent-protocol-reference.md offset=57 limit=55
```

---

---

## Test-Driven Development Requirements

**MANDATORY:** All code changes MUST use the perform-tdd skill.

### perform-tdd Skill Invocation

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/perform_tdd/entry.py --algorithm-state {session_id}
```

### Quick Commands (after venv activation)

```bash
cd .claude/orchestration
source .venv/bin/activate
```

| Gate | Command |
|------|---------|
| Run tests | `make test` |
| Format | `make format` |
| Lint | `make lint` |

### TDD Cycle

| Phase | Gate Requirement |
|-------|------------------|
| **RED** | Test exists AND fails |
| **GREEN** | All tests pass |
| **REFACTOR** | Tests pass + `make lint` = 10/10 |
| **DOC** | Documentation updated |

### Test File Locations

| Source File | Test File |
|-------------|-----------|
| `entry_base.py` | `tests/unit/orchestration/test_entry_base.py` |
| `flow_invoker.py` | `tests/unit/orchestration/test_flow_invoker.py` |
| `state/config.py` | `tests/unit/orchestration/state/test_config.py` |
| `state/base.py` | `tests/unit/orchestration/state/test_base.py` |
| `state/algorithm_fsm.py` | `tests/unit/orchestration/state/test_algorithm_fsm.py` |
| `state/algorithm_state.py` | `tests/unit/orchestration/state/test_algorithm_state.py` |
| `skills/perform_tdd/tdd_state.py` | `tests/unit/orchestration/skills/perform_tdd/test_tdd_state.py` |
| `utils.py` | `tests/unit/orchestration/test_utils.py` |
| `agent_chain/flow.py` | `tests/unit/orchestration/agent_chain/test_flow.py` |
| `agent_chain/state.py` | `tests/unit/orchestration/agent_chain/test_state.py` |
| `agent_chain/memory.py` | `tests/unit/orchestration/agent_chain/test_memory.py` |
| `agents/config.py` | `tests/unit/orchestration/agents/test_config.py` |
| `decompose/flows.py` | `tests/unit/orchestration/decompose/test_flows.py` |
| `decompose/complete.py` | `tests/unit/orchestration/decompose/test_complete.py` |
| `decompose/entry.py` | `tests/unit/orchestration/decompose/test_entry.py` |

### Reference

- **perform-tdd Skill:** `.claude/skills/perform-tdd/SKILL.md`
- **TDD Protocol:** `.claude/research/tdd-protocol.md`

---

*Last updated: 2026-01-31*
