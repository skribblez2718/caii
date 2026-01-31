# DECOMPOSE: Synthesis

## Context

Generate the final subtask list as a JSON array.
Each subtask MUST be SIMPLE complexity - this is non-negotiable.

---

## Critical Requirements

1. **ALL subtasks MUST be SIMPLE**
   - If a subtask is moderate+, decompose it further
   - No exceptions - SIMPLE only

2. **Valid Dependency Graph (DAG)**
   - No circular dependencies
   - Dependencies reference valid subtask IDs
   - At least one subtask has no dependencies (entry point)

3. **Complete Coverage**
   - Subtasks cover 100% of parent task scope
   - No gaps in functionality
   - No duplicate coverage

4. **Clear Boundaries**
   - Each subtask has distinct scope
   - Minimal overlap between subtasks
   - Clear handoff points

---

## Output Format

Generate JSON array of subtasks:

```json
[
  {
    "subtask_id": "ST-001",
    "description": "Clear, actionable description of what to accomplish",
    "complexity": "simple",
    "dependencies": [],
    "verification_criteria": [
      "Specific, testable criterion 1",
      "Specific, testable criterion 2"
    ],
    "context": {
      "from_parent": "Relevant context from parent task",
      "technical_notes": "Any technical considerations"
    }
  },
  {
    "subtask_id": "ST-002",
    "description": "Second subtask description",
    "complexity": "simple",
    "dependencies": ["ST-001"],
    "verification_criteria": [
      "Criterion for this subtask"
    ],
    "context": {
      "from_parent": "Relevant context",
      "depends_on_output": "What ST-001 produces that this needs"
    }
  }
]
```

---

## Subtask ID Convention

- Format: `ST-NNN` (e.g., ST-001, ST-002)
- Sequential numbering
- Stable IDs (don't renumber)

## Verification Criteria Guidelines

- Specific and testable
- No vague terms ("should work", "is good")
- Measurable where possible
- Include edge cases if relevant

## Output Focus

Provide ONLY the JSON array - no additional commentary.
The JSON will be parsed programmatically by complete_decomposition().
