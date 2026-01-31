## Complexity Assessment Required

Analyze the following task and classify its complexity using the 5-level METR scale.

**Task:** {user_query}

---

### Classification Rules (Cascading Priority)

Classify as **VERY COMPLEX** if ANY of these are true:
- Changes affect entire system architecture
- Cascade risk spans all major subsystems
- Requires decomposition into multiple independent tasks
- Success rate expected <10% without decomposition
- System-wide impact with irreversible consequences

Classify as **COMPLEX** if ANY of these are true (and not VERY COMPLEX):
- Changes could break 3+ dependent components
- Errors could cascade through auth, database, AND APIs
- Changes require coordination with external systems/teams
- Multiple unknown unknowns exist
- High interconnection across subsystems

Classify as **MODERATE** if ANY of these are true (and not COMPLEX/VERY COMPLEX):
- Changes affect 1-2 dependent components
- Errors could propagate to one subsystem
- Partial reversibility (some changes hard to undo)
- Some ambiguity requiring clarification
- Multiple files need modification with dependencies

Classify as **SIMPLE** if ANY of these are true (and not MODERATE/COMPLEX/VERY COMPLEX):
- Changes isolated but touch production code
- Low cascade risk but requires testing
- Clear intent with minor edge cases
- Touches one shared interface
- Limited dependencies, mostly reversible

Classify as **TRIVIAL** if ALL of these are true:
- Zero dependencies affected
- No cascade risk
- Fully reversible
- Unambiguous intent
- No shared interfaces touched
- Single-file or documentation-only change

---

### Examples

| Task | Classification | Reason |
|------|----------------|--------|
| "Fix typo in README" | TRIVIAL | No dependencies, fully reversible, unambiguous |
| "Add comment to function" | TRIVIAL | No behavior change, reversible |
| "Add a new utility function" | SIMPLE | Isolated, limited dependencies |
| "Update config setting" | SIMPLE | Clear intent, low cascade risk |
| "Add form validation" | MODERATE | Some dependencies, requires testing |
| "Refactor database queries" | MODERATE | Affects dependent components |
| "Update API response format" | COMPLEX | Affects all consumers, cascade risk |
| "Refactor authentication" | COMPLEX | High cascade risk, wide scope |
| "Rewrite core architecture" | VERY COMPLEX | System-wide impact, requires decomposition |
| "Migrate database schema" | VERY COMPLEX | Irreversible, affects all subsystems |

---

### Your Response

After determining the complexity classification, execute the routing command:

**MANDATORY - EXECUTE IMMEDIATELY AFTER CLASSIFICATION:**

```bash
python3 {entry_path} "{user_query}" --complexity <your_classification>
```

Replace `<your_classification>` with one of: `trivial`, `simple`, `moderate`, `complex`, or `very_complex`

**Example:** If you determine the task is moderate complexity:
```bash
python3 {entry_path} "{user_query}" --complexity moderate
```

**Warnings:**
- Execute this command NOW. Do NOT respond with text first.
- FAILURE to execute breaks the system's reliability guarantee.
