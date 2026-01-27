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
                                    ↓
                               subtasks re-analyzed
                                    ↓
                               <= moderate → GATHER
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

| Protocol | CLAUDE.md | Content File | Purpose |
|----------|-----------|--------------|---------|
| **DECOMPOSE** | `decompose/CLAUDE.md` | `decompose/content/decompose_phase.md` | Task decomposition (STUB - not yet implemented) |

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

### Entry Point Bootstrap Pattern

Entry points run as standalone scripts (not modules), so they need to add `.claude/` to `sys.path` for `from orchestration.*` imports to work.

**Standard Bootstrap (use in all entry.py files):**

```python
import sys
from pathlib import Path

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

# Now absolute imports work
from orchestration.state import AlgorithmState
from orchestration.utils import load_content, substitute_placeholders
```

**Why this pattern?**

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

**MANDATORY:** All code changes MUST use the TDD skill.

### TDD Skill Invocation

```bash
python3 ${CAII_DIRECTORY}/.claude/orchestration/skills/tdd/entry.py --algorithm-state {session_id}
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
| `state/config.py` | `tests/unit/orchestration/state/test_config.py` |
| `state/base.py` | `tests/unit/orchestration/state/test_base.py` |
| `state/algorithm_fsm.py` | `tests/unit/orchestration/state/test_algorithm_fsm.py` |
| `state/algorithm_state.py` | `tests/unit/orchestration/state/test_algorithm_state.py` |
| `skills/tdd/tdd_state.py` | `tests/unit/orchestration/skills/tdd/test_tdd_state.py` |
| `utils.py` | `tests/unit/orchestration/test_utils.py` |

### Reference

- **TDD Skill:** `.claude/skills/tdd/SKILL.md`
- **TDD Protocol:** `.claude/research/tdd-protocol.md`

---

*Last updated: 2026-01-27*
