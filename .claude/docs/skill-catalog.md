# Skill Catalog

**Purpose:** Quick reference for all available skills in the system.

---

## Skill Types

| Type | Description | Invocation |
|------|-------------|------------|
| **Composite Skills** | Multi-phase workflows using multiple cognitive agents | Skill Orchestration Protocol |
| **Atomic Skills** | Single-agent wrappers for individual cognitive functions | Dynamic Skill Sequencing |

---

## Composite Skills

Composite skills orchestrate multiple cognitive agents through defined phase sequences.

### develop-learnings

**Purpose:** Transform completed workflow experiences into structured, reusable learnings organized by cognitive function.

**When to Use:**
- Post-workflow capture of insights and patterns
- Unknown→Known transitions that should become permanent knowledge
- Pattern preservation for future agent improvement
- Anti-pattern identification to avoid future mistakes

**Location:** `${CAII_DIRECTORY}/.claude/skills/develop-learnings/`

---

### develop-skill

**Purpose:** Meta-skill for creating and updating workflow skills using 6 universal cognitive agents. Supports composite-to-composite skill composition.

**When to Use:**
- New workflow pattern needed for a task type
- Existing skill needs enhancement or modification
- Agent sequencing design for new task patterns
- System capability extension

**Location:** `${CAII_DIRECTORY}/.claude/skills/develop-skill/`

---

### develop-command

**Purpose:** Create and manage Claude Code slash commands for utility operations.

**When to Use:**
- New utility command needed for a specific operation
- Adding command to existing category
- Building composite command that calls other commands
- Updating or maintaining existing commands

**Location:** `${CAII_DIRECTORY}/.claude/skills/develop-command/`

---

## Atomic Skills (orchestrate-*)

Atomic skills wrap single cognitive agents for use in Dynamic Skill Sequencing. Each maps to exactly one cognitive function.

| Skill | Cognitive Function | Purpose |
|-------|-------------------|---------|
| orchestrate-clarification | CLARIFIER | Transform vague inputs into actionable specifications |
| orchestrate-research | RESEARCHER | Investigate options, gather domain knowledge |
| orchestrate-analysis | ANALYZER | Decompose problems, assess complexity, identify risks |
| orchestrate-synthesis | SYNTHESIZER | Integrate findings into coherent recommendations |
| orchestrate-generation | GENERATOR | Create artifacts using TDD methodology |
| orchestrate-validation | VALIDATOR | Verify artifacts against quality criteria |
| orchestrate-memory | METACOGNITION | Monitor progress, detect impasses, suggest remediation |

### When to Use Atomic Skills

Atomic skills are building blocks for Dynamic Skill Sequencing when:
- Task requires multiple cognitive functions but doesn't match a composite skill
- Flexible orchestration is needed for novel task patterns
- Single cognitive function needs isolated invocation

### Example Skill Sequences

| Task Type | Atomic Skill Sequence |
|-----------|----------------------|
| Research task | orchestrate-clarification → orchestrate-research → orchestrate-synthesis |
| Analysis task | orchestrate-analysis → orchestrate-synthesis → orchestrate-validation |
| Complex task | orchestrate-clarification → orchestrate-research → orchestrate-analysis → orchestrate-synthesis → orchestrate-generation → orchestrate-validation |

### Location

All atomic skills located at: `${CAII_DIRECTORY}/.claude/skills/orchestrate-*/`

---

## Skill Selection Guide

### Decision Tree

```
Does task match a composite skill pattern?
├── YES → Use Skill Orchestration Protocol with matching composite skill
└── NO → Does task require multiple cognitive functions?
         ├── YES → Use Dynamic Skill Sequencing with atomic skills
         └── NO → Does task pass triviality criteria?
                  ├── YES → Use Direct Execution
                  └── NO → Use single atomic skill or escalate
```

### Quick Reference

| Task Pattern | Recommended Skill |
|--------------|-------------------|
| "Create a new skill for Z" | develop-skill |
| "Capture what we learned" | develop-learnings |
| "Create a utility command" | develop-command |
| Novel multi-step task | Dynamic Skill Sequencing |

---

## Related Documentation

- `${CAII_DIRECTORY}/.claude/docs/execution-protocols.md` - Protocol details
- `${CAII_DIRECTORY}/.claude/docs/cognitive-function-taxonomy.md` - Agent functions
- `${CAII_DIRECTORY}/.claude/DA.md` - System prompt with skill definitions
