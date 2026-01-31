---
paths:
  - ".claude/agents/**"
---

# Agent Development Guidelines

## 7 Cognitive Agents

The system uses 7 universal cognitive agents that adapt to ANY task domain:

| Agent | Cognitive Function | Primary Use |
|-------|-------------------|-------------|
| **research** | RESEARCH | Information discovery and evaluation |
| **analysis** | ANALYSIS | Decomposition, risk assessment, dependencies |
| **synthesis** | SYNTHESIS | Integration, design, contradiction resolution |
| **generation** | GENERATION | Artifact creation (code, docs, plans) |
| **validation** | VALIDATION | Quality verification, compliance checking |
| **clarification** | CLARIFICATION | Ambiguity resolution, requirements refinement |
| **memory** | METACOGNITION | Progress tracking, impasse detection |

## Agent File Structure

Each agent definition in `.claude/agents/{agent}.md` contains:

```markdown
---
name: {agent_name}
description: "{brief description}"
tools: {allowed tools}
model: {opus|sonnet|haiku}
color: {status color}
---

# Identity
## Capabilities
## Context Adaptation
# Execution Protocol
# Quality Standards
# Output Artifacts
# Output Format
```

## Domain Adaptation

Agents adapt to 5 domains while maintaining consistent cognitive processes:

| Domain | Focus Areas |
|--------|-------------|
| **Technical** | Security, performance, test coverage, code quality |
| **Personal** | Value alignment, life balance, wellbeing |
| **Creative** | Audience engagement, narrative coherence, originality |
| **Professional** | Business value, stakeholder needs, ROI |
| **Recreational** | Fun, engagement, accessibility |

## Token Budget

All agents have STRICT token limits:
- **Total:** 5,000 tokens maximum
- **Johari Summary:** ~1,200 tokens
- **Step Overview:** ~750 tokens
- **Remaining:** ~3,050 tokens

## Memory File Output (MANDATORY)

Every agent MUST write a memory file before completing:

```
Path: .claude/memory/{task-id}-{agent}-memory.md

Sections:
- Section 0: Context Loaded (JSON)
- Section 1: Step Overview
- Section 2: Johari Summary (JSON)
- Section 3: Downstream Directives
- Section 4: User Questions (if needed)
```

## Standard Workflow Sequence

```
clarification → research → analysis → synthesis → generation → validation
```

## Agent Creation Policy

DO NOT create new agents unless:
- A fundamental cognitive function is missing
- Proposed agent would be reusable across 5+ workflow types
- Current agents cannot adapt to handle the cognitive need
