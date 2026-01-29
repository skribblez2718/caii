# Agents Execution Module

Infrastructure for agent execution within the orchestration system.

---

## Directory Structure

```
agents/
├── CLAUDE.md             # This file
├── __init__.py           # Module exports
├── config.py             # AGENT_REGISTRY and utilities
├── base.py               # AgentExecutionState dataclass
├── entry.py              # agent_entry() function
├── complete.py           # agent_complete() function
└── state/                # Runtime agent state files (gitignored)
```

---

## Agent Registry

Seven cognitive agents are registered:

| Agent | Cognitive Function | Model | Description |
|-------|-------------------|-------|-------------|
| `clarification` | CLARIFICATION | sonnet | Transform vague inputs into actionable specs |
| `research` | RESEARCH | sonnet | Systematic information discovery |
| `analysis` | ANALYSIS | opus | Decompose complexity, identify patterns |
| `synthesis` | SYNTHESIS | opus | Integrate info into coherent designs |
| `generation` | GENERATION | sonnet | Create artifacts |
| `validation` | VALIDATION | sonnet | Verify artifacts against criteria |
| `memory` | METACOGNITION | haiku | Impasse detection and remediation |

---

## Learning Injection

**CRITICAL:** Every agent MUST scan learnings before any cognitive work.

Learning injection is now handled at the **agent level** via a MANDATORY directive at the end of each agent's `.md` file. Agents scan their learnings files directly rather than relying on Python injection.

### Learnings Location

```
.claude/learnings/{agent_name}/
├── .gitkeep
├── heuristics.md      # Decision heuristics
├── anti-patterns.md   # What to avoid
└── checklists.md      # Verification checklists
```

### INDEX Format

```markdown
## INDEX (Always Loaded)
- R-H-001 - Cache API responses to avoid rate limits
- R-H-002 - Verify SSL certs in production research

---

## Full Entries Below
### R-H-001: Cache API Responses
**Situation:** When making repeated API calls
**Principle:** Cache responses locally
```

---

## AgentExecutionState

Tracks execution state for an agent:

```python
@dataclass
class AgentExecutionState:
    agent_name: str           # e.g., "research"
    task_id: str              # Unique task identifier
    current_step: int         # Current step number
    skill_name: Optional[str] # Invoking skill
    phase_id: Optional[str]   # Phase within skill
    flow_id: Optional[str]    # Agent chain flow ID
    context_pattern: str      # How to load predecessor context
    predecessors: List[str]   # Predecessor agent names
    step_outputs: Dict        # Step outputs by number
    completed_steps: List     # Completed step numbers
```

---

## Entry and Complete Functions

### agent_entry()

Initializes agent execution:

1. Parses arguments (task_id, skill context, predecessors)
2. Creates AgentExecutionState
3. Saves state
4. Prints initialization message

```python
from orchestration.agents.entry import agent_entry

# Called by Task tool when agent is invoked
agent_entry("research")
```

### agent_complete()

Finalizes agent execution:

1. Loads execution state
2. Verifies memory file exists
3. Updates state with completion metadata
4. Prints completion marker
5. Prints next agent directive (if in flow)

```python
from orchestration.agents.complete import agent_complete

# Called when agent finishes work
agent_complete("research")
```

---

## Context Budgets

Token limits per agent (from ACT-R buffer constraints):

| Agent | Max Input | Max Output | Priority Sections |
|-------|-----------|------------|-------------------|
| clarification | 2000 | 1500 | task_description, user_query, unknowns |
| research | 3000 | 2500 | research_queries, unknowns, constraints |
| analysis | 2500 | 2000 | research_findings, constraints, trade_offs |
| synthesis | 3000 | 2500 | analysis_output, constraints, design_decisions |
| generation | 4000 | 8000 | specification, design, constraints |
| validation | 2500 | 1500 | artifact, criteria, constraints |
| memory | 1500 | 800 | agent_output_summary, previous_goal_state |

---

## Agent Name Aliases

Old names map to canonical names:

| Alias | Canonical |
|-------|-----------|
| `clarification-agent` | `clarification` |
| `research-agent` | `research` |
| `goal-memory-agent` | `memory` |

Use `normalize_agent_name()` for compatibility.

---

## Key Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `get_agent_config(name)` | `config.py` | Get agent configuration |
| `get_agent_budget(name)` | `config.py` | Get context token budget |
| `normalize_agent_name(name)` | `config.py` | Normalize to canonical name |
| `is_valid_agent(name)` | `config.py` | Check if agent exists |
| `agent_entry(name)` | `entry.py` | Initialize agent execution |
| `agent_complete(name)` | `complete.py` | Finalize agent execution |

---

## Tests

Located at: `tests/unit/orchestration/agents/`

- `test_config.py` - AGENT_REGISTRY tests

Run tests:

```bash
source .venv/bin/activate
pytest tests/unit/orchestration/agents/ -v
```

---

*Last updated: 2026-01-28*
