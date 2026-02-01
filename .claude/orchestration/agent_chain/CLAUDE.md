# Agent Chain Module

Infrastructure for agent invocation and chaining. Agents pass context to each other via memory files, enabling complex multi-agent workflows without hub-and-spoke communication.

---

## Architecture

```
DA invokes first agent with protocol content
         │
         ▼
    ┌─────────────────┐
    │ ChainOrchestrator│
    │ checks: first   │
    │ invocation?     │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
YES (first)      NO (subsequent)
    │                 │
    ▼                 │
┌─────────────────┐   │
│ Inject MANDATORY│   │
│ Learnings       │   │
│ Directive       │   │
└────────┬────────┘   │
         │            │
         └─────┬──────┘
               │
               ▼
    ┌─────────────────┐
    │ Build Agent     │
    │ Invocation      │
    │ Directive       │
    └────────┬────────┘
             │
             ▼
    ┌─────────┐     memory file      ┌─────────┐     memory file      ┌─────────┐
    │ Agent A │ ──────────────────▶ │ Agent B │ ──────────────────▶ │ Agent C │
    └─────────┘                      └─────────┘                      └─────────┘
         │                                │                                │
    reads:                           reads:                           reads:
    - learnings directive            - learnings directive            - protocol content
      (first time only)                (first time only)                (no learnings -
    - protocol content               - protocol content                 already loaded)
    - system prompt                  - A's memory file                - B's memory file
```

**Key**: Agent's complete prints directive for next agent. DA follows directives.

---

## Directory Structure

```
agent_chain/
├── CLAUDE.md           # This file
├── __init__.py         # Module exports
├── flow.py             # FlowStep, AgentFlow, ContextPattern
├── state.py            # ChainState tracking
├── memory.py           # MemoryFile, load_predecessor_context()
├── invoker.py          # build_agent_invocation_directive()
├── orchestrator.py     # ChainOrchestrator class
├── dynamic.py          # create_dynamic_flow() for DA
└── state/              # Runtime chain state files (gitignored)
```

---

## Key Components

### FlowStep

Defines a single step in an agent flow:

```python
@dataclass(frozen=True)
class FlowStep:
    agent_name: str                    # e.g., "clarification"
    context_pattern: ContextPattern    # How to load predecessor context
    predecessors: Tuple[str, ...]      # Agents to load context from
    content_file: Optional[str]        # Path to protocol content
    conditional: bool = False          # May be skipped at runtime
```

### AgentFlow

Defines a complete agent flow:

```python
@dataclass(frozen=True)
class AgentFlow:
    flow_id: str           # e.g., "perform-tdd-red"
    name: str              # "TDD RED Phase"
    steps: Tuple[FlowStep, ...]
    source: str            # "skill" or "dynamic"
```

### ContextPattern

How an agent loads predecessor context:

| Pattern | Description |
|---------|-------------|
| `WORKFLOW_ONLY` | No predecessor memory files (first agent) |
| `IMMEDIATE_PREDECESSORS` | Load from single immediate predecessor |
| `MULTIPLE_PREDECESSORS` | Load from multiple specified predecessors |

### ChainOrchestrator

Manages flow execution:

```python
orchestrator = ChainOrchestrator(
    flow=TDD_RED_FLOW,
    task_id="abc123",
    skill_content_dir=Path("skills/perform_tdd/content"),
    skill_name="perform-tdd",
    phase_id="red",
)

# Start the flow
directive = orchestrator.start_flow()

# After agent completes
next_directive = orchestrator.get_next_directive("clarification")
```

---

## Memory File Protocol

**Path**: `.claude/memory/{task_id}-{agent_name}-memory.md`

```markdown
# {Agent} Agent Output

## Section 0: Context Loaded
{task_id, flow_id, predecessors_loaded}

## Section 1: Step Overview
{Summary of work performed}

## Section 2: Johari Summary
{Known Knowns, Known Unknowns, Unknown Unknowns}

## Section 3: Downstream Directives
{Instructions for next agent - THIS IS WHAT NEXT AGENT READS}

---
**{AGENT_NAME}_COMPLETE**
```

---

## Learnings Injection Protocol

Every agent MUST scan learnings before any cognitive work. Learnings are injected via a MANDATORY directive prepended to the agent's prompt on their **first invocation** within a flow.

### When Injected

- **First time** an agent is invoked in a flow (tracked via `ChainState.learnings_injected_for`)
- **NOT** on subsequent invocations of the same agent in the same flow

### What is Injected

A directive instructing the agent to:
1. Scan INDEX sections from `.claude/learnings/{agent}/`
2. Identify relevant learning IDs based on task context
3. Read full entries for relevant IDs
4. Apply learnings to their cognitive work

### State Tracking

`ChainState.learnings_injected_for` persists which agents have received the directive.

### Implementation Flow

```python
# In ChainOrchestrator._build_directive_for_step():

# Check if this agent needs learnings directive
include_learnings = self.state.needs_learnings_directive(step.agent_name)

# Mark BEFORE building (crash safety)
if include_learnings:
    self.state.mark_learnings_injected(step.agent_name)
    self.state.save()

# Build directive with learnings flag
directive = build_agent_invocation_directive(
    ...,
    include_learnings_directive=include_learnings,
)
```

### Learnings File Structure

**Location**: `.claude/learnings/{agent_name}/`

**Files Scanned**:
- `heuristics.md` - Decision heuristics
- `anti-patterns.md` - What to avoid
- `checklists.md` - Verification checklists

**INDEX Format** (always loaded, ~200-400 tokens):

```markdown
## INDEX (Always Loaded)
- R-H-001 - Cache API responses to avoid rate limits
- R-H-002 - Verify SSL certs in production research
---
```

---

## Creating Dynamic Flows

For novel tasks not covered by predefined skills:

```python
from orchestration.agent_chain.dynamic import create_dynamic_flow

flow = create_dynamic_flow(
    name="Custom Analysis",
    agent_sequence=["clarification", "research", "analysis"],
)
```

With explicit context configuration:

```python
from orchestration.agent_chain.dynamic import create_dynamic_flow_with_context

flow = create_dynamic_flow_with_context(
    name="Complex Flow",
    steps_config=[
        ("clarification", "WORKFLOW_ONLY", []),
        ("research", "IMMEDIATE_PREDECESSORS", ["clarification"]),
        ("analysis", "MULTIPLE_PREDECESSORS", ["clarification", "research"]),
    ],
)
```

---

## Usage Example

### 1. Define a Flow (in skill's flows.py)

```python
TDD_RED_FLOW = AgentFlow(
    flow_id="perform-tdd-red",
    name="TDD RED Phase",
    source="skill",
    steps=(
        FlowStep(
            agent_name="clarification",
            context_pattern=ContextPattern.WORKFLOW_ONLY,
            content_file="red/clarification.md",
            conditional=True,
        ),
        FlowStep(
            agent_name="research",
            context_pattern=ContextPattern.IMMEDIATE_PREDECESSORS,
            predecessors=("clarification",),
            content_file="red/research.md",
        ),
        # ...
    ),
)
```

### 2. Start Flow (RECOMMENDED: use flow_invoker.py)

**Preferred pattern** - use the shared utility for consistent flow invocation:

```python
from orchestration.flow_invoker import invoke_agent_flow

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

### Alternative: Direct ChainOrchestrator

Only use when you need advanced orchestrator control:

```python
orchestrator = ChainOrchestrator(
    flow=TDD_RED_FLOW,
    task_id=state.session_id,
    skill_content_dir=CONTENT_DIR,
    skill_name="perform-tdd",
    phase_id="red",
)

directive = orchestrator.start_flow()
print(directive)
```

### 3. Agent Invocation Directive

The directive includes (in order):
1. **Learnings Directive** (first invocation only) - MANDATORY section at TOP
2. **Protocol Instructions** (from content file)
3. **Predecessor Context** (from memory files)
4. **Memory Output Requirements**

Learnings injection is handled automatically by `ChainOrchestrator._build_directive_for_step()`.

---

## Flow Continuation

When an agent completes, the flow continues via `flow_continue.py`:

```
Agent completes
      │
      ▼
agents/complete.py
      │
      ▼ (subprocess call)
flow_continue.py --task-id <id> --completed-agent <name>
      │
      ├── Load ChainState
      ├── Look up flow in flow_registry
      ├── Call orchestrator.get_next_directive()
      │
      ├── If more agents → Print Task tool directive
      └── If done → Print FLOW_COMPLETE marker
```

### Flow Registry

All flows are registered in `flow_registry.py` for ID-based lookup:

```python
from orchestration.flow_registry import get_flow, list_flows

flow = get_flow("perform-tdd-red")  # Returns AgentFlow
all_ids = list_flows()  # Returns ["perform-tdd-red", ...]
```

### FLOW_COMPLETE Marker

When all agents in a flow have completed, `flow_continue.py` prints:

```
**FLOW_COMPLETE: {flow_id}**

All agents in flow have completed.
Ready for {skill_name} phase advancement.
```

This unambiguous marker signals to DA that the current phase is ready for advancement.

---

## Critical Invariants

```
⚠️  INVARIANTS - VIOLATING THESE BREAKS THE SYSTEM

1. Learnings Injection is MANDATORY (First Invocation Only)
   └→ ChainOrchestrator injects learnings directive on first agent invocation
   └→ Tracked via ChainState.learnings_injected_for
   └→ State saved BEFORE directive built (crash safety)
   └→ No exceptions, no bypasses

2. Agents NEVER invoked without protocol content
   └→ content/{phase}/{agent}.md provides instructions
   └→ Directive builder loads and includes this content

3. Memory file MUST exist before agent_complete() succeeds
   └→ Verified before printing next agent directive

4. Agent chains via directive, NOT via DA
   └→ complete prints next directive
   └→ DA just executes what it sees
```

---

## File Reference

| File | Purpose |
|------|---------|
| `flow.py` | FlowStep, AgentFlow, ContextPattern dataclasses |
| `state.py` | ChainState for tracking execution |
| `memory.py` | MemoryFile class, load_predecessor_context() |
| `invoker.py` | build_agent_invocation_directive() |
| `orchestrator.py` | ChainOrchestrator class |
| `dynamic.py` | create_dynamic_flow() and helpers |

---

*Last updated: 2026-01-31*
