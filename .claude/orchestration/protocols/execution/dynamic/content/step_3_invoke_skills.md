# Invoke Skills in Sequence

Execute each orchestrate-* skill according to the planned sequence.

## Instructions

For each skill in the sequence, invoke it using the Skill tool.

### Skill Invocation Protocol

For each skill in sequence:

1. **Check Skip Condition**
   - If skip condition is met, record skip and continue to next skill
   - If not skipped, proceed with invocation

2. **Invoke Skill**
   - Use the Skill tool with the skill name
   - Example: `Skill(skill="orchestrate-analysis")`
   - The skill will internally use the Task tool with the appropriate agent

3. **Record Output**
   - Each skill writes its output to a memory file
   - Verify the memory file was created
   - Note any errors or issues

4. **Continue Sequence**
   - Pass context to next skill via the memory file
   - Proceed to next skill in sequence

### Skill to Agent Mapping

| Skill | Agent (via Task tool) |
|-------|----------------------|
| orchestrate-clarification | clarification |
| orchestrate-research | research |
| orchestrate-analysis | analysis |
| orchestrate-synthesis | synthesis |
| orchestrate-generation | generation |
| orchestrate-validation | validation |

### Error Handling

If a skill fails:
1. Record the error
2. Determine if sequence can continue
3. If critical failure, abort and report
4. If recoverable, attempt retry (max 1)

### Output Requirements

For each skill invoked, record:

```
SKILL: orchestrate-{name}
STATUS: [INVOKED | SKIPPED | FAILED]
REASON: {why invoked/skipped/failed}
OUTPUT: {summary of output or error message}
```

## Important Notes

- WAIT for each skill to complete before proceeding to next
- Do NOT run skills in parallel unless explicitly designed for it
- Each skill may take significant time - be patient
