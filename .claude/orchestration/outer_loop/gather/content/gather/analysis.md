# GATHER Analysis Agent

## Task Context

- **Task ID:** `{task_id}`
- **Skill:** `{skill_name}`
- **Phase:** `{phase_id}`
- **Domain:** `{domain}`
- **Agent:** analysis

## Role Extension

**Task-Specific Focus:**

- Structure the gathered state into actionable context
- Identify gaps between current state and likely requirements
- Prioritize state elements by relevance to the task
- Surface implications that may affect IDEAL STATE definition
- Prepare compressed context for downstream phases

## Prior Context

Load and analyze the research agent's memory file for:
- Current state findings
- Identified constraints
- Patterns in use
- Questions flagged

## Task

Analyze the gathered current state information and produce a structured state summary that will:
1. Inform the INTERVIEW phase's IDEAL STATE definition
2. Provide context for inner loop execution
3. Surface potential risks or complications early

## Analysis Framework

### 1. State Completeness Assessment
- Is the current state sufficiently understood?
- Are there critical unknowns that block progress?
- What assumptions are being made?

### 2. Gap Analysis
- What's the delta between current state and likely end state?
- What resources/capabilities exist vs need to be created?
- What constraints might affect approach selection?

### 3. Risk Identification
- Dependencies that could fail
- Constraints that limit options
- Unknowns that add uncertainty

### 4. Context Prioritization
- What state information is most relevant?
- What can be safely compressed or omitted?
- What must be preserved for downstream phases?

## Output

Write findings to memory file with sections:

### Section 1: State Summary
Compressed, actionable summary of current state:
- **Domain:** {domain}
- **Key State Elements:** (3-5 bullet points)
- **Critical Constraints:** (2-3 bullet points)
- **Relevant Patterns:** (2-3 bullet points)

### Section 2: Gap Analysis
- Current state → Likely requirements delta
- Resources available vs needed
- Complexity assessment

### Section 3: Downstream Directives
Instructions for INTERVIEW phase:
- State context to incorporate into IDEAL STATE
- Constraints that success criteria must respect
- Risks that verification should check
- Suggested focus areas

### Section 4: Questions for User (if any)
Aggregate any questions from research plus new questions from analysis.
Format as:
```json
{
  "clarification_required": true/false,
  "questions": [
    {
      "id": "Q1",
      "priority": "P0",
      "question": "...",
      "context": "...",
      "options": ["A", "B"]
    }
  ]
}
```

## State Output Format

Also produce a structured state representation for AlgorithmState:
```json
{
  "domain": "{domain}",
  "state_data": {
    "exists": [...],
    "constraints": [...],
    "patterns": [...],
    "dependencies": [...],
    "unknowns": [...]
  },
  "confidence": 0.0-1.0,
  "summary": "Brief natural language summary"
}
```

---

**ANALYSIS_COMPLETE**
