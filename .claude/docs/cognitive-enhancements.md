# Cognitive Enhancements Documentation

**Purpose:** Reference documentation for Penny's cognitive architecture enhancements inspired by ACT-R and Soar cognitive architectures.

---

## Overview

Penny implements four major cognitive enhancements that enable learning, metacognition, and sustainable multi-agent workflows:

| Enhancement | Purpose | Inspiration |
|-------------|---------|-------------|
| GoalMemory Agent | Detect impasses, track goals, suggest remediation | Soar impasse detection |
| Utility Tracking | Learn from routing outcomes | ACT-R utility learning |
| Episodic Memory | Reuse patterns across tasks | Soar episodic memory |
| Context Budgets | Enforce cognitive capacity limits | Working memory constraints |

---

## 1. GoalMemory Agent (METACOGNITION)

### Purpose

A metacognitive monitor that tracks problem-solving state and detects when progress has stalled. Unlike other agents that Penny invokes directly, memory agent is **automatically invoked** by the Python orchestration layer.

### Invocation Points

- **After each agent completes:** `common_complete.py` triggers assessment
- **At phase transitions:** `advance_phase.py` triggers skill-level assessment

### Impasse Types (Based on Soar)

| Type | Description | Typical Response |
|------|-------------|------------------|
| **CONFLICT** | Contradictory requirements or constraints | Invoke clarification or escalate |
| **MISSING-KNOWLEDGE** | Required information is absent | Invoke research |
| **TIE** | Multiple valid options, insufficient criteria | Invoke analysis or escalate |
| **NO-CHANGE** | Agent output shows no meaningful progress | Re-invoke with enhanced context |

### Detection Threshold

- Impasse is detected when GoalMemory confidence >= 0.7
- Maximum remediation loops: 3 per impasse

### Output Schema

```json
{
  "goal_state": {
    "primary_goal": "string",
    "active_subgoals": [],
    "constraints": {"hard": [], "soft": []},
    "problem_state_summary": "string"
  },
  "progress_assessment": {
    "progress_made": true|false,
    "progress_indicators": [],
    "stall_indicators": []
  },
  "impasse_detection": {
    "impasse_detected": true|false,
    "impasse_type": "none|no-change|tie|conflict|missing-knowledge",
    "confidence": 0.0-1.0
  },
  "remediation_recommendation": {
    "action": "continue|re-invoke|escalate|clarify|abort",
    "target_agent": "string",
    "rationale": "string"
  }
}
```

### Key Files

- `${PAI_DIRECTORY}/.claude/agents/memory.md` - Agent definition
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/agent/common_complete.py` - Agent-level invocation
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/advance_phase.py` - Phase-level invocation

---

## 2. Utility Tracking (ACT-R Inspired)

### Purpose

Learn from routing outcomes to improve future decisions. Implements ACT-R's utility calculation: `U = P × G - C` where:
- **U** = Utility score
- **P** = Probability of success (based on historical outcomes)
- **G** = Goal value (importance/priority)
- **C** = Cost (tokens, time)

### How It Works

1. **Event Logging:** Each workflow completion logs success/failure, tokens used, time taken
2. **Score Calculation:** Utility scores maintained per route/agent combination
3. **Recommendations:** System can recommend optimal agents based on utility scores

### CLI Interface

```bash
# Log a utility event
python utility_tracker.py log --task-id TASK-123 --outcome success --tokens 5000 --time 120

# Get utility score for an agent
python utility_tracker.py score analysis --context coding

# Get statistics
python utility_tracker.py stats

# Get recommendations
python utility_tracker.py recommend --task-type research
```

### Key Files

- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/utility_tracker.py` - Utility tracking system
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/completion_signals.py` - Completion logging

---

## 3. Episodic Memory (Soar Inspired)

### Purpose

Store and retrieve successful problem-solving patterns for reuse across similar tasks. When a new task arrives, the system searches for similar past episodes to inform approach.

### How It Works

1. **Episode Capture:** After successful workflow completion, episode is stored with:
   - Task description and context
   - Agent sequence used
   - Outcome and metrics
   - Key decisions made

2. **Similarity Matching:** Uses Jaccard similarity on tokenized task descriptions

3. **Pattern Retrieval:** Similar episodes provide:
   - Recommended agent sequences
   - Known pitfalls to avoid
   - Successful approaches to reuse

### CLI Interface

```bash
# Store an episode
python episodic_memory.py store --task-id TASK-123

# Search for similar episodes
python episodic_memory.py search "create REST API with authentication"

# Get statistics
python episodic_memory.py stats

# Export episodes
python episodic_memory.py export --format json
```

### Integration Point

Episodic retrieval is integrated in `step_5_trigger_agents.py` during skill orchestration. Before invoking agents, the system searches for similar past episodes to inform the approach.

### Key Files

- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/episodic_memory.py` - Episodic memory system
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/episodic_retrieval.py` - Retrieval utilities

---

## 4. Context Budgets

### Purpose

Enforce token limits per agent to ensure sustainable multi-agent workflows. Prevents context overflow and maintains consistent agent performance.

### Budget Configuration

| Agent | Max Input Tokens | Max Output Tokens |
|-------|------------------|-------------------|
| clarification | 2,000 | 1,500 |
| research | 3,000 | 2,500 |
| analysis | 2,500 | 2,000 |
| synthesis | 3,000 | 2,500 |
| generation | 4,000 | 8,000 |
| validation | 2,500 | 1,500 |
| memory agent | 1,500 | 800 |

### Enforcement

- `base_agent_step.py` contains `enforce_context_budget()` function
- Token counting uses tiktoken with fallback estimation
- Over-budget content is compressed using priority-based pruning

### Key Files

- `${PAI_DIRECTORY}/.claude/orchestration/protocols/agent/config.py` - AGENT_CONTEXT_BUDGETS configuration
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/agent/base_agent_step.py` - Budget enforcement

---

## Integration Architecture

### Python vs LLM Boundary

**Python (orchestration layer) controls:**
- WHETHER to invoke GoalMemory (always after agents)
- WHETHER impasse threshold met (confidence >= 0.7)
- HOW MANY remediation loops allowed (max 3)
- WHICH utility scores to use (deterministic calculation)
- HOW MUCH context to pass (budget enforcement)

**LLM (agents) determines:**
- WHAT the goal state looks like (GoalMemory interprets)
- WHY an impasse occurred (GoalMemory diagnoses)
- HOW to recover from impasse (GoalMemory suggests)
- WHAT content to generate (cognitive agents produce)

### Execution Flow

```
TASK ARRIVAL
    │
    ├──► Check episodic memory for similar tasks
    │
    └──► Create memory file with initial goal_state

FOR EACH AGENT EXECUTION:
    │
    ├──► Enforce context budget
    │
    ├──► Execute cognitive agent
    │
    ├──► Execute GoalMemory agent (automatic)
    │
    ├──► Parse GoalMemory output
    │
    ├──► Check impasse (confidence >= 0.7?)
    │    ├── YES → Handle impasse (re-invoke/clarify/escalate/abort)
    │    └── NO  → Continue to gate evaluation
    │
    └──► Log utility event

TASK COMPLETION
    │
    ├──► Store episode to episodic memory
    │
    ├──► Recalculate utility scores
    │
    └──► Archive memory file
```

---

## Configuration

Enhancement configuration is centralized in protocols/skill/config.py:

```python
SKILL_ENHANCEMENT_CONFIG = {
    "goal_memory": {
        "enabled": True,
        "impasse_threshold": 0.7,
        "max_remediation_loops": 3
    },
    "utility_tracking": {
        "enabled": True,
        "log_directory": "utility_logs/"
    },
    "episodic_memory": {
        "enabled": True,
        "store_directory": "episodic_memory/",
        "similarity_threshold": 0.3
    },
    "context_budgets": {
        "enabled": True,
        "enforcement_mode": "compress"  # or "warn" or "fail"
    }
}
```

---

## Related Documentation

- `${PAI_DIRECTORY}/.claude/docs/cognitive-function-taxonomy.md` - METACOGNITION function definition
- `${PAI_DIRECTORY}/.claude/docs/agent-registry.md` - memory agent entry
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/agent/config.py` - Agent budget configuration
- `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/config.py` - Skill enhancement configuration
