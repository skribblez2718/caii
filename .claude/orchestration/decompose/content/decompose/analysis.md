# DECOMPOSE: Analysis

## Context

Identify decomposition axes and candidate subtasks for a complex task.
Goal: Find natural boundaries where the task can be split into SIMPLE pieces.

---

## Decomposition Strategies

Analyze the task using these decomposition axes:

### 1. Functional Decomposition
Split by feature or capability:
- Independent features
- Distinct behaviors
- Separate concerns

### 2. Component Decomposition
Split by architectural component:
- UI layer
- Business logic
- Data layer
- Infrastructure

### 3. Sequential Decomposition
Split by phases or stages:
- Setup phase
- Implementation phase
- Testing phase
- Integration phase

### 4. Parallel Decomposition
Split by independent work streams:
- Tasks with no dependencies
- Tasks that can run concurrently
- Tasks owned by different concerns

---

## Analysis Checklist

- [ ] All decomposition axes evaluated
- [ ] Natural boundaries identified
- [ ] Candidate subtasks enumerated
- [ ] Dependencies between candidates mapped
- [ ] Each candidate can be SIMPLE complexity

## Complexity Reduction Criteria

Each subtask MUST be reducible to SIMPLE:
- Clear, focused scope
- 1-2 main objectives
- Minimal dependencies
- Can be completed in isolation

## Output Focus

Provide:
- List of candidate subtasks
- Decomposition axis used for each
- Preliminary dependency graph
- Complexity assessment per subtask
