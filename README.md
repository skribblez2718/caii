# CAII - Cognitive Augmented Intelligence Infrastructure

## Acknowledgments

This project is built upon the foundational work and inspiration from **Daniel Miessler's Personal AI Infrastructure (PAI)** project. Without his knowledge, vision, and open sharing of ideas, this project would likely not exist.

[danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure/)

While CAII shares PAI's goal of providing a highly customizable system to augment humans with AI, it takes a fundamentally different approach. Grounded in research and experimentation, this implementation sometimes diverges from popular opinion and Claude Code documentation. Notable differences include:

- **Cognitive-first agent design** - Rather than task or domain-specific agents, CAII uses agents organized by cognitive function (clarification, research, analysis, synthesis, generation, validation, memory). This idea is roughly rooted in ACr and Soar approaches that I discovered after coming up with the cognitive approach, but is the memory agent and learning systems became heavily influenced by them. 
- **External skill protocols** - Skill orchestration logic lives in Python protocols rather than within SKILL.md files
- **Mandatory Python orchestration** - A Python layer enforces protocol adherence through deterministic state machines, rather than relying on prompting alone. 
- **Johari Window framework** - Systematic discovery using the SHARE/ASK/ACKNOWLEDGE/EXPLORE model to surface unknowns, ensure they are considered and hopefully answered at the end of task completion

This is an experimental approach that may not suit every use case, but it represents one possible direction for human-AI augmentation systems.

---

![Cognitive Augmented Intelligence Infrastructure](img/caii.png)

---

> **Note:** This project is in active development and should be considered experimental. APIs, protocols, and behaviors may change as the system evolves. Contributions and feedback are welcome.

---

## Table of Contents

1. [Overview](#overview)
2. [The Johari Window Approach](#the-johari-window-approach)
3. [Core Philosophy](#core-philosophy)
4. [Architecture Overview](#architecture-overview)
5. [The Directing Agent (DA)](#the-directing-agent-da)
6. [Reasoning Protocol](#reasoning-protocol)
7. [Deterministic Orchestration + Non-Deterministic Execution](#deterministic-orchestration--non-deterministic-execution)
8. [Execution Routes](#execution-routes)
9. [Cognitive Domain Agents](#cognitive-domain-agents)
10. [Skills Architecture](#skills-architecture)
11. [Memory and Learnings System](#memory-and-learnings-system)
12. [Extending the System](#extending-the-system)
13. [Prompt Flags](#prompt-flags)
14. [Directory Structure](#directory-structure)
15. [Quick Start](#quick-start)

---

## Overview

CAII is a **cognitive orchestration framework** for Claude Code that transforms how AI assistants approach complex tasks. Instead of relying on ad-hoc prompting, CAII enforces systematic reasoning through Python-orchestrated protocols before any task execution.

**Core value proposition:**
- **Systematic reasoning** - Every query goes through a 9-step reasoning protocol automatically
- **Domain-adaptive agents** - 7 cognitive agents that adapt to any domain without modification
- **Progressive learning** - The system learns from each workflow, requiring less instruction over time

**Key differentiator:** CAII combines Python-enforced deterministic orchestration (guaranteed step sequences) with LLM non-determinism (creative execution within each step). This ensures protocol adherence while preserving the flexibility that makes LLMs powerful.

```
                              USER QUERY
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   REASONING PROTOCOL     │
                    │   (9 Steps: 0-8)         │
                    │   Runs AUTOMATICALLY     │
                    └──────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌───────────────┐          ┌──────────────────┐
           │    SKILL      │          │    DYNAMIC       │
           │ ORCHESTRATION │          │ SKILL SEQUENCING │
           └───────────────┘          └──────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   COGNITIVE AGENTS       │
                    │   (7 Specialists)        │
                    └──────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   MEMORY FILES           │
                    │   + LEARNINGS            │
                    └──────────────────────────┘
```

---

## The Johari Window Approach

CAII is built around the **Johari Window** framework for systematic discovery. The core mission: **transform unknown unknowns into known knowns**.

### The Four Quadrants

| Quadrant | What It Represents | Action |
|----------|-------------------|--------|
| **Open** | Known knowns - what both parties understand | Share explicitly |
| **Hidden** | Known unknowns - what we know we don't know | Ask to discover |
| **Blind** | Unknown knowns - gaps we don't realize exist | Acknowledge through probing |
| **Unknown** | Unknown unknowns - what neither party recognizes | Explore systematically |

### The SHARE/ASK/ACKNOWLEDGE/EXPLORE Framework

Every interaction begins with Step 0 of the reasoning protocol, which applies this framework:

- **SHARE** - What can be inferred from the user's prompt
- **ASK** - What critical information is missing (max 5 clarifying questions)
- **ACKNOWLEDGE** - Boundaries, assumptions, and constraints
- **EXPLORE** - Unknown unknowns that should be considered

### Why This Matters

The Johari Window approach prevents:
- **Premature execution** - Acting before understanding
- **Assumption errors** - Building on unstated requirements
- **Scope creep** - Missing boundaries and constraints
- **Blind spots** - Overlooking critical considerations

**Mission statement:** "Every interaction must advance collective understanding or it has failed."

---

## Core Philosophy

CAII is built on five non-negotiable principles that guide all system design decisions.

### Principle 1: Radical Modularity

Every component performs **ONE task exceptionally well**. This is the Single Cognitive Responsibility Principle (SCRP):

- Each agent handles exactly one cognitive function
- Components can be understood in isolation
- Dependencies are minimal and explicit

### Principle 2: Orchestration-Implementation Separation

The boundary between WHAT and HOW is sacred:

- **Skills** define WHAT happens (workflow orchestration, phase sequences)
- **Agents** define HOW tasks execute (implementation details)
- Skills NEVER contain implementation logic
- Agents NEVER contain workflow orchestration

### Principle 3: Zero Redundancy

- Never repeat system definitions, protocols, or references
- Create reference files for shared elements
- Single point of change for all system components
- If something is used twice, it becomes a reference file

### Principle 4: Token Efficiency

Maximize succinctness without sacrificing necessary detail:

- Progressive context compression between phases
- Johari Window format with strict token limits (1,200 max per agent)
- Decision-focused documentation (WHAT was decided, not HOW)
- Reference previous findings rather than repeating them

### Principle 5: Systematic Reasoning

ALL agents implement these prompting strategies:

| Strategy | Purpose |
|----------|---------|
| **Chain of Thought (CoT)** | Explicit step-by-step reasoning |
| **Tree of Thought (ToT)** | Multiple solution path exploration |
| **Self-Consistency** | Cross-verification of conclusions |
| **Socratic Method** | Self-interrogation for clarity |
| **Constitutional AI** | Self-critique against principles |

---

## Architecture Overview

CAII operates as a layered system where each layer has distinct responsibilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐    ┌───────────────────┐    ┌────────────┐  │
│  │     DA.md      │◄──►│     Python        │◄──►│   Hooks    │  │
│  │  (Coordination │    │  Orchestration    │    │  (Entry    │  │
│  │   Framework)   │    │     Layer         │    │   Points)  │  │
│  └────────────────┘    └───────────────────┘    └────────────┘  │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      PROTOCOLS                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │  Reasoning   │  │  Execution   │  │    Agent     │    │   │
│  │  │  (9 Steps)   │  │  (2 Routes)  │  │  (7 Agents)  │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       SKILLS                              │   │
│  │  ┌────────────────┐        ┌────────────────┐            │   │
│  │  │  Atomic Skills │        │   Composite    │            │   │
│  │  │  (7 wrappers)  │        │    Skills      │            │   │
│  │  └────────────────┘        └────────────────┘            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**How the pieces connect:**

1. **Hooks** intercept user prompts and trigger the Python orchestration layer
2. **Python Orchestration** enforces protocol adherence through mandatory directives
3. **Protocols** define the step sequences for reasoning, execution, and agents
4. **Skills** orchestrate which agents to invoke and in what order
5. **Agents** perform the actual cognitive work
6. **Memory/Learnings** persist knowledge between sessions

---

## The Directing Agent (DA)

### What the DA is NOT

- NOT an executing agent that performs tasks
- NOT one of the 7 cognitive agents
- NOT invoked via the Task tool

### What the DA IS

The DA is a **coordination framework** defined in `DA.md` that:

- Establishes the system's identity and mission
- Orchestrates the 6 task-performing agents through Python orchestration
- Enforces the mandatory reasoning protocol before any task execution
- Routes tasks to the appropriate execution path

### Key Responsibilities

| Responsibility | Description |
|---------------|-------------|
| **Enforce Reasoning** | Every query goes through 9 steps (0-8) automatically |
| **Route Tasks** | Direct to Skill Orchestration or Dynamic Skill Sequencing |
| **Maintain Discovery** | Apply Johari Window principles to every interaction |
| **Verify Outputs** | Apply confidence scoring and assumption declaration |

### Default Behavior

**The reasoning protocol executes for EVERY user query.** This is automatic, not optional. The `user-prompt-submit` hook triggers the reasoning protocol before Claude sees any prompt.

---

## Reasoning Protocol

The reasoning protocol is a **9-step sequence (Steps 0-8)** that runs automatically for every user query. This ensures systematic reasoning before any task execution.

```
Step 0: Johari Window Discovery
        │
        ▼
Step 1: Semantic Understanding
        │
        ▼
Step 2: Chain of Thought
        │
        ▼
Step 3: Tree of Thought
        │
        ▼
Step 3b: Skill Detection
        │
        ▼
Step 4: Task Routing ──────────────────┐
        │                              │
        ▼                              │ (Skipped in Agent Mode)
Step 5: Self-Consistency               │
        │                              │
        ▼                              │
Step 6: Socratic Interrogation         │
        │                              │
        ▼                              │
Step 7: Constitutional Critique        │
        │                              │
        ▼                              │
Step 8: Knowledge Transfer ◄───────────┘
        │
        ├──► PROCEED (dispatch to execution)
        │
        ├──► HALT (ask clarifying questions)
        │
        └──► LOOP_BACK (contradiction detected, retry Steps 4-8)
```

### Step Descriptions

| Step | Name | Purpose |
|------|------|---------|
| 0 | Johari Discovery | Apply SHARE/ASK/ACKNOWLEDGE/EXPLORE framework |
| 1 | Semantic Understanding | Parse and understand the query's meaning |
| 2 | Chain of Thought | Break down the problem step-by-step |
| 3 | Tree of Thought | Explore multiple solution paths |
| 3b | Skill Detection | Identify if a known skill pattern matches |
| 4 | Task Routing | Determine execution route (skill vs dynamic) |
| 5 | Self-Consistency | Cross-verify conclusions for coherence |
| 6 | Socratic Interrogation | Challenge assumptions through questioning |
| 7 | Constitutional Critique | Verify against system principles |
| 8 | Knowledge Transfer | Final checkpoint with PROCEED/HALT/LOOP_BACK |

### Critical Rule

**If Step 0 identifies clarifying questions, the protocol HALTS and asks before proceeding.** This prevents wasted effort on tasks with unclear requirements.

### Agent Mode

When agents execute (they're already routed), they use `--agent-mode` which skips Step 4:
```
Steps: 0 → 1 → 2 → 3 → 3b → 5 → 6 → 7 → 8
                        (Step 4 skipped)
```

---

## Deterministic Orchestration + Non-Deterministic Execution

### The Problem with Prompting Alone

Prompting alone **cannot guarantee strict protocol adherence**. LLMs may:

- Skip steps when they seem unnecessary
- Reorder operations based on perceived efficiency
- Combine steps that should be separate
- Forget to save state before proceeding

### The Solution: Python Orchestration

Python scripts output **mandatory Markdown directives** that Claude must execute:

```
**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**
`python3 step_1_semantic_understanding.py --state {file}`

DO NOT proceed with any other action until this command is executed.
```

### Key Enforcement Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| `format_mandatory_directive()` | Wraps commands in enforcement language |
| **FSM (Finite State Machine)** | Validates legal state transitions |
| **State Persistence** | State saved BEFORE printing next directive |
| **Blocking Verification** | Phase advancement blocks until memory file exists |

### What's Deterministic vs Non-Deterministic

| Deterministic (Python Enforced) | Non-Deterministic (LLM Flexibility) |
|--------------------------------|-------------------------------------|
| Step sequence (always 0-8) | Content of each step's output |
| State transitions | Creative reasoning within steps |
| Memory file creation | How to phrase clarifying questions |
| Phase advancement | Solution design decisions |
| Skill selection routing | Code generation approaches |

### Crash Recovery

Because state is persisted before directives are printed:
- If crash occurs mid-step: Resume from saved state
- Session ID enables recovery: `entry.py --resume {session_id}`

---

## Execution Routes

After the reasoning protocol completes, execution flows through ONE of two routes.

### Route 1: Skill Orchestration

Used when the task matches a **formal skill pattern** (e.g., "create a new skill").

```
Reasoning Step 4 Output: "skill-orchestration"
    │
    ▼
protocols/execution/skill/entry.py
    │
    ▼
Phase 0 (Clarification) → Phase 1 → ... → Phase N
    │
    ▼
Each phase invokes: orchestrate-{agent} atomic skill
    │
    ▼
Agent produces memory file
    │
    ▼
advance_phase.py (BLOCKS until memory file exists)
```

### Route 2: Dynamic Skill Sequencing

Used when the task requires **multiple cognitive functions but doesn't match an existing skill**.

```
Reasoning Step 4 Output: "dynamic-skill-sequencing"
    │
    ▼
protocols/execution/dynamic/entry.py
    │
    ▼
1. Analyze Requirements
2. Plan Sequence (determine which orchestrate-* skills)
3. Invoke Skills (sequence of atomic skills)
4. Verify Completion
5. Complete
```

### Trivial Task Handling

The **routing gate** evaluates 5 triviality criteria. ALL must be YES for direct execution:

| Criterion | Question |
|-----------|----------|
| SINGLE_FILE | Does task affect only one file? |
| FIVE_LINES_OR_LESS | Does task change 5 lines or fewer? |
| MECHANICAL_OPERATION | Is it purely mechanical (no judgment)? |
| NO_RESEARCH_NEEDED | No information gathering required? |
| NO_DECISIONS_NEEDED | Zero judgment calls needed? |

**Fail-Secure Design:** If ANY criterion is uncertain, default to AGENT_REQUIRED.

---

## Cognitive Domain Agents

CAII uses **7 cognitive agents**, each specializing in exactly one cognitive function.

### Agent Roster

| Agent | Cognitive Function | Purpose |
|-------|-------------------|---------|
| **clarification** | CLARIFICATION | Transform vague inputs into actionable specifications |
| **research** | RESEARCH | Discover and gather information from sources |
| **analysis** | ANALYSIS | Examine information to identify patterns, risks, issues |
| **synthesis** | SYNTHESIS | Integrate disparate findings into coherent designs |
| **generation** | GENERATION | Create artifacts using TDD methodology |
| **validation** | VALIDATION | Verify artifacts against quality criteria |
| **memory** | METACOGNITION | Monitor progress, detect impasses (automatic invocation) |

### Single Cognitive Responsibility Principle (SCRP)

Each agent performs **exactly ONE cognitive function**. This is non-negotiable because:

1. **Maintainability** - 7 agents to maintain vs potentially dozens of task-specific agents
2. **Reusability** - Same agent works across any domain
3. **Composability** - Combine agents into workflows without overlap
4. **Testability** - Each function can be validated independently

### Domain Adaptation

Agents adapt to ANY domain while maintaining consistent methodology:

| Domain | Same Methodology | Different Evaluation Criteria |
|--------|-----------------|------------------------------|
| Technical | Socratic questioning | Architecture, security, performance |
| Personal | Socratic questioning | Values, goals, priorities |
| Creative | Socratic questioning | Tone, audience, message |
| Professional | Socratic questioning | Business objectives, stakeholders |
| Recreational | Socratic questioning | Preferences, inclusivity |

The cognitive PROCESS stays constant; only the VOCABULARY and SUCCESS CRITERIA change.

### Agent Invocation Pattern

Agents are **NEVER invoked directly**. The call chain is:

```
Skill Phase → orchestrate-{agent} (atomic skill) → Task tool → Agent Entry
```

---

## Skills Architecture

Skills define **workflow orchestration** - the sequence of cognitive agents to invoke and when.

### Two Skill Types

| Type | Description | Example |
|------|-------------|---------|
| **Atomic** | Single-agent wrappers for individual cognitive functions | orchestrate-clarification |
| **Composite** | Multi-phase workflows using multiple agents | develop-skill |

### 7 Atomic Skills

Each wraps exactly one cognitive agent:

| Skill | Agent | Purpose |
|-------|-------|---------|
| orchestrate-clarification | clarification | Transform vague inputs into specifications |
| orchestrate-research | research | Investigate options, gather domain knowledge |
| orchestrate-analysis | analysis | Decompose problems, assess complexity |
| orchestrate-synthesis | synthesis | Integrate findings into recommendations |
| orchestrate-generation | generation | Create artifacts using TDD |
| orchestrate-validation | validation | Verify artifacts against criteria |
| orchestrate-memory | memory | Monitor progress, detect impasses |

### 2 Built-in Composite Skills

| Skill | Purpose | Phases |
|-------|---------|--------|
| **develop-skill** | Meta-skill for creating new skills | 6 phases |
| **develop-learnings** | Transform experiences into reusable learnings | 7 phases |

### Phase Types

| Type | Behavior |
|------|----------|
| LINEAR | Standard sequential execution (default) |
| OPTIONAL | Skip if trigger condition not met |
| ITERATIVE | Execute sub-phases in sequence (e.g., 3A→3B→3C) |
| REMEDIATION | Retry on validation failure (max 2 retries) |
| PARALLEL | Execute branches concurrently, merge results |

### Skill-to-Skill Composition

Skills can invoke other skills, enabling complex workflows through composition rather than monolithic definitions.

---

## Memory and Learnings System

### Goal: Progressive Autonomy

The memory system's purpose is to **tell the system less over time**. As learnings accumulate, the system requires fewer explicit instructions and makes better decisions autonomously.

### Memory File Contract

Every agent MUST produce a memory file at:
```
.claude/memory/{task_id}-{agent}-memory.md
```

**Mandatory sections:**

| Section | Content |
|---------|---------|
| Section 0: Context Loaded | JSON verification of what was loaded |
| Section 1: Step Overview | What was accomplished, key decisions |
| Section 2: Johari Summary | Open/Hidden/Blind/Unknown (1,200 tokens max) |
| Section 3: Downstream Directives | Instructions for next agent/phase |

**Critical:** Phase advancement **BLOCKS** until the memory file exists. There is no bypass mechanism.

### Learnings Directory Structure

```
.claude/learnings/
├── clarification/
│   ├── heuristics.md
│   ├── anti-patterns.md
│   ├── checklists.md
│   └── domain-snippets/
├── research/
├── analysis/
├── synthesis/
├── generation/
└── validation/
```

### Learning Types

| Type | Purpose |
|------|---------|
| **heuristics** | Rules of thumb that improve decisions |
| **anti-patterns** | Mistakes to avoid |
| **checklists** | Verification steps |
| **domain-snippets** | Domain-specific knowledge |

### Learning Injection (Step 0)

Every agent's Step 0 loads relevant learnings before task work:

```
Step 0: Learning Injection
    │
    ▼
Load .claude/learnings/{cognitive_function}/*.md
    │
    ▼
Inject relevant learnings into agent context
    │
    ▼
Step 1: Begin actual work
```

### Impasse Detection

The memory agent monitors for four impasse types:

| Impasse | Description | Remediation |
|---------|-------------|-------------|
| CONFLICT | Contradictory requirements | Invoke clarification |
| MISSING-KNOWLEDGE | Required info absent | Invoke research |
| TIE | Multiple valid options, no criteria | Invoke analysis |
| NO-CHANGE | No meaningful progress | Re-invoke with enhanced context |

### Creating Learnings

Learnings are created via the **develop-learnings** skill after workflows complete:

```
Completed Workflow → develop-learnings skill → 7 phases → Learnings committed
```

---

## Extending the System

CAII provides only the **minimum required skills** out of the box. The system is designed as a foundation for building domain-specific extensions.

### Creating New Skills

Use the **develop-skill** meta-skill:

```
User: "Create a code-review skill"
    │
    ▼
develop-skill workflow (6 phases)
    │
    ▼
1. Requirements Clarification
2. Complexity Analysis
3. Pattern Research
4. Design Synthesis
5. Skill Generation
6. DA.md Registration
    │
    ▼
New skill ready to use
```

### Skill Templates

Located in `.claude/skills/develop-skill/resources/`:

| Template | Use Case |
|----------|----------|
| simple-skill-template.md | 2-3 phases, straightforward workflow |
| complex-skill-template.md | 4+ phases, conditional logic |
| atomic-skill-template.md | Single agent wrapper |

### What Gets Generated

For a new composite skill:

```
.claude/skills/{skill-name}/
├── SKILL.md                    # Skill definition
└── resources/                  # Skill-specific resources

.claude/orchestration/protocols/skill/composite/{skill_name}/
├── entry.py                    # Entry point
├── complete.py                 # Completion handler
├── __init__.py                 # Module init
└── content/
    ├── phase_0_*.md
    ├── phase_1_*.md
    └── ...
```

Plus registration in:
- `config/config.py` (phase definitions)
- `DA.md` (semantic triggers)
- `skill-catalog.md` (documentation)

---

## Prompt Flags

CAII supports prompt flags that modify how queries are processed. Flags can appear in any order at the end of a prompt.

### Available Flags

| Flag | Purpose |
|------|---------|
| `-i` | Improve prompt via external model before processing |
| `-b` | Bypass reasoning protocol (direct execution mode) |

### Examples

```
"fix the bug -b"         → Bypass reasoning, execute directly
"add feature -i"         → Improve prompt, then run reasoning
"refactor code -i -b"    → Improve prompt, then bypass reasoning
"refactor code -b -i"    → Same as above (order doesn't matter)
```

### Prompt Improvement (-i flag)

The `-i` flag sends your prompt to an external model for improvement before processing:

```
User: "build me a web app -i"
    │
    ▼
Hook detects "-i" flag
    │
    ▼
Sends to external model for improvement
    │
    ▼
Returns improved prompt
    │
    ▼
Normal reasoning protocol continues (unless -b also specified)
```

**Configuration** - Required environment variables:

```bash
OPENAI_BASE_URL="https://your-api-endpoint"
OPENAI_API_KEY="your-key"
OPENAI_PROMPT_IMPROVER_MODEL="model-name"
```

The `-i` flag supports Johari Window discovery by making implicit requirements explicit and transforming unknown unknowns in the prompt itself.

### Bypass Mode (-b flag)

The `-b` flag skips the 9-step reasoning protocol entirely, allowing Claude to handle the prompt directly. Useful for:

- Trivial tasks (typo fixes, simple renames)
- Follow-up prompts where context is already established
- Quick questions that don't require systematic reasoning

**Note:** The `-b` flag bypasses all reasoning steps, so use it when you're confident the task doesn't benefit from structured analysis.

---

## Directory Structure

```
.claude/
├── DA.md                           # Directing Agent definition
├── settings.json                   # Configuration
│
├── agents/                         # 7 agent definitions
│   ├── clarification.md
│   ├── research.md
│   ├── analysis.md
│   ├── synthesis.md
│   ├── generation.md
│   ├── validation.md
│   └── memory.md
│
├── docs/                           # System documentation
│   ├── philosophy.md               # Core principles
│   ├── cognitive-function-taxonomy.md
│   ├── skill-catalog.md
│   └── ...
│
├── hooks/                          # Claude Code hooks
│   ├── user-prompt-submit/         # Entry point for all queries
│   ├── session-start/              # Session initialization
│   └── ...
│
├── learnings/                      # Progressive learning storage
│   ├── clarification/
│   ├── research/
│   ├── analysis/
│   ├── synthesis/
│   ├── generation/
│   └── validation/
│
├── memory/                         # Workflow memory files (gitignored)
│
├── orchestration/                  # Python orchestration layer
│   ├── protocols/
│   │   ├── reasoning/              # 9-step reasoning protocol
│   │   ├── execution/              # Post-reasoning execution
│   │   ├── agent/                  # Agent protocol implementations
│   │   └── skill/                  # Skill definitions
│   └── shared/                     # Reusable content
│
└── skills/                         # Skill definitions
    ├── develop-skill/              # Meta-skill for creating skills
    ├── develop-learnings/          # Learning capture skill
    └── orchestrate-*/              # 7 atomic skills
```

---

## Quick Start

### Prerequisites

- Claude Code CLI installed
- Project directory with `.claude/` structure from this repository

### Basic Usage

1. **Start a conversation** - Any query triggers the reasoning protocol automatically
   ```
   User: "Help me build an authentication system"
   ```

2. **Expect clarifying questions** - Step 0 may identify unknowns
   ```
   Claude: "Before proceeding, I need to understand:
            1. What authentication methods? (OAuth, JWT, session-based)
            2. What's the target platform?
            ..."
   ```

3. **Provide answers** - System resumes from where it halted

4. **Observe structured execution** - Tasks route through cognitive agents systematically

### Using Prompt Improvement

```
User: "build me a thing -i"
```

### Viewing Memory Files

```bash
ls .claude/memory/
cat .claude/memory/{task_id}-{agent}-memory.md
```

### Key Points

- **Reasoning runs automatically** - You don't need to invoke it
- **Clarification is expected** - The system asks before assuming
- **State persists** - Workflows can be resumed
- **Learnings accumulate** - The system improves over time

---

## TODO

### Known Issues

- **Inconsistent reasoning protocol triggers after plan mode exit** - The reasoning protocol sometimes fails to trigger consistently when exiting plan mode. Fix implemented (PostToolUse hook) but not yet verified.
- **Skill orchestration invoked for direct execution work** - Determine why skill orchestration is sometimes triggered for tasks that should be handled via direct tool execution. Analyze routing gate logic and triviality evaluation.

### Documentation

- **Add setup/usage instructions to README** - Comprehensive setup guide including prerequisites, installation, configuration, and first-run instructions
- **Document environment variables and their usage** - Create reference for all required and optional environment variables (CAII_DIRECTORY, DA_NAME, OPENAI_*, VOICE_SERVER_PORT, etc.)

### UI/UX Improvements

- **Remove banners from skill orchestration** - Clean up verbose banner output during skill orchestration protocol execution

### Voice Integration

- **Create voice-server GitHub repo** - Publish the text-to-speech voice server that supports the stop hook notifications as a standalone repository
- **Integrate speech-to-text** - Add speech-to-text capability to complement the existing text-to-speech functionality for full voice interaction

### Ongoing

- **System benchmarking** - Establish metrics and benchmarks to measure reasoning quality, task completion rates, and system performance
- Continuous improvement of agent prompts and learnings
- Expansion of domain-specific learnings as the system is used
- Performance optimization of orchestration layer
