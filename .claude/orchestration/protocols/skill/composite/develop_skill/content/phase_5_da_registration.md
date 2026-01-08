# Phase 5: Documentation Registration (Comprehensive)

**Agent:** Penny (direct execution, not cognitive agent)
**Phase Type:** LINEAR

## Purpose

Register the new/updated skill across ALL documentation touchpoints to ensure system-wide consistency and discoverability.

## Workflow Mode Handling

Check `metadata.workflow_mode` from Phase 0:

- **CREATE mode:** Add new entries to all required documentation
- **UPDATE mode:** Update existing entries based on `metadata.update_scope`

---

## Documentation Updates

### 1. DA.md Registration (REQUIRED)

**Location:** `${PAI_DIRECTORY}/.claude/DA.md`

**Actions:**
1. Read DA.md and locate the "Execution Routing" section
2. Find appropriate subsection:
   - If `type: atomic` → "Atomic Skills" subsection
   - If `type: composite` → "Composite Skills" subsection
3. Add skill entry in alphabetical order

**Entry Format for Composite Skills:**

```markdown
#### {skill-name}

**Purpose:** {one-line description}

**When to Use:** Invoke when **{primary trigger pattern}**:

- **{Trigger 1}:** {Description} → "{Example user utterance}"
- **{Trigger 2}:** {Description} → "{Example user utterance}"
- **{Trigger 3}:** {Description} → "{Example user utterance}"
- **{Trigger 4}:** {Description} → "{Example user utterance}"
- **{Trigger 5}:** {Description} → "{Example user utterance}"
```

**Entry Format for Atomic Skills:**

```markdown
| {function} | orchestrate-{function} |
```

**IMPORTANT:** Must include exactly 5 semantic trigger examples for composite skills.

---

### 2. skill-catalog.md Registration (REQUIRED)

**Location:** `${PAI_DIRECTORY}/.claude/docs/skill-catalog.md`

**Actions:**
1. Read skill-catalog.md
2. Find appropriate section (Composite Skills or Atomic Skills)
3. Add entry in alphabetical order

**Entry Format:**

```markdown
### {skill-name}

**Purpose:** {one-line description}

**Type:** {composite|atomic}

**When to Use:**
- {Use case 1}
- {Use case 2}
- {Use case 3}

**Location:** `.claude/skills/{skill-name}/`

**Orchestration:** `.claude/orchestration/protocols/skill/composite/{skill_name}/`
```

---

### 3. composite/CLAUDE.md Update (REQUIRED for composite skills)

**Location:** `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/composite/CLAUDE.md`

**Actions:**
1. Find the "Registered Composite Skills" table
2. Add new row in alphabetical order

**Table Entry Format:**

```markdown
| {skill-name} | {phase_count} | {purpose} | {key_phases} |
```

**Example:**
```markdown
| my-skill | 5 | Process user requests | clarification → analysis → generation |
```

---

### 4. protocols/skill/CLAUDE.md Update (CONDITIONAL)

**Location:** `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/CLAUDE.md`

**Update if:**
- New phase types introduced
- New execution patterns established
- Significant changes to skill execution flow

**Actions if updating:**
1. Update "Composite Skills" table in the registries section
2. Add any new phase type documentation
3. Update call chain diagrams if flow changed

---

### 5. Other Documentation (CONDITIONAL)

Check and update if relevant:

#### agent-registry.md
**Location:** `${PAI_DIRECTORY}/.claude/docs/agent-registry.md`
**Update if:** Skill introduces new agent interaction patterns

#### execution-protocols.md
**Location:** `${PAI_DIRECTORY}/.claude/docs/execution-protocols.md`
**Update if:** Skill introduces new execution patterns

#### cognitive-function-taxonomy.md
**Location:** `${PAI_DIRECTORY}/.claude/docs/cognitive-function-taxonomy.md`
**Update if:** Skill reveals new cognitive function patterns

---

### 6. config.py Registration (MANUAL - from Phase 3)

**Location:** `${PAI_DIRECTORY}/.claude/orchestration/protocols/skill/config/config.py`

**Actions:**
1. Retrieve config.py registration code from Phase 3 generation output
2. Present code for manual review
3. Instruct user to insert:
   - COMPOSITE_SKILLS entry
   - Phase definition dict
   - SKILL_PHASES mapping

**IMPORTANT:** This is a MANUAL step. Do not auto-inject into config.py.

---

## Documentation Consistency Checklist

Before completing this phase, verify:

- [ ] All documentation uses consistent skill name (hyphenated)
- [ ] All documentation uses consistent description
- [ ] Alphabetical ordering maintained in all lists/tables
- [ ] No duplicate entries created
- [ ] All cross-references are valid
- [ ] Formatting matches existing entries

---

## Gate Exit Criteria

### CREATE Mode - All Required
- [ ] DA.md updated with skill entry
- [ ] DA.md entry includes 5 semantic triggers
- [ ] skill-catalog.md updated with entry
- [ ] composite/CLAUDE.md table updated (if composite)
- [ ] config.py registration code presented for manual insertion
- [ ] All formatting consistent with existing entries
- [ ] Alphabetical ordering maintained

### UPDATE Mode - Per Scope
- [ ] All documentation in update_scope has been modified
- [ ] Changes are consistent across all updated files
- [ ] No orphaned references created

---

## Output

1. **Documentation Updates Completed:**
   - List all files modified with specific changes made

2. **Manual Steps Required:**
   - config.py registration (present code for insertion)

3. **Verification:**
   - Confirm all gate exit criteria met
   - Document any issues or warnings

4. **Memory File:**
   - Record all documentation updates in memory file
   - Note any follow-up actions required
