# scaffold-docs Skill Orchestration

Python-based orchestration for documentation scaffolding workflow.

---

## Directory Structure

```
skills/scaffold_docs/
├── __init__.py               # Package exports
├── CLAUDE.md                 # This file
├── scaffold_docs_state.py    # ScaffoldDocsPhase, ScaffoldDocsFSM, ScaffoldDocsState
├── flows.py                  # Agent flow definitions
├── entry.py                  # Main entry point
├── detector.py               # Language/framework detection
├── language_defaults.py      # Per-language defaults
├── content/
│   ├── scaffold/             # Agent content for scaffold mode
│   │   ├── clarification.md
│   │   ├── analysis.md
│   │   ├── synthesis.md
│   │   └── validation.md
│   └── update/               # Agent content for update mode
│       ├── analysis.md
│       ├── synthesis.md
│       └── validation.md
└── state/                    # Runtime state files (gitignored)
```

---

## Agent Flow Architecture

Two modes with different flows:

```
     SCAFFOLD Mode
    ┌─────────────────┐
    │  clarification  │ (gather project info)
    │       ↓         │
    │    analysis     │ (analyze codebase)
    │       ↓         │
    │    synthesis    │ (generate docs)
    │       ↓         │
    │   validation    │ (verify best practices)
    └─────────────────┘

      UPDATE Mode
    ┌─────────────────┐
    │    analysis     │ (detect changes)
    │       ↓         │
    │    synthesis    │ (update docs)
    │       ↓         │
    │   validation    │ (verify no regression)
    └─────────────────┘
```

---

## Flow Definitions (flows.py)

| Flow | Flow ID | Agents |
|------|---------|--------|
| `SCAFFOLD_FLOW` | `scaffold-docs-scaffold` | clarification → analysis → synthesis → validation |
| `UPDATE_FLOW` | `scaffold-docs-update` | analysis → synthesis → validation |

---

## State Management

### ScaffoldDocsPhase Enum

```
INITIALIZED -> CLARIFICATION -> ANALYSIS -> SYNTHESIS -> VALIDATION -> COMPLETED
                    │                                          ▲
                    └──────────────(update mode skips)─────────┘
```

### ScaffoldDocsState Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | str | 12-char unique identifier |
| `parent_algorithm_id` | str | Link to parent AlgorithmState |
| `target_path` | str | Target project directory |
| `mode` | str | 'scaffold' or 'update' |
| `detected_language` | str | Detected language |
| `project_config` | Dict | User answers from clarification |
| `created_files` | List | Files created during execution |
| `updated_files` | List | Files updated during execution |
| `fsm` | ScaffoldDocsFSM | State machine |
| `phase_outputs` | Dict | Outputs recorded per phase |

### FSM Transitions

| Mode | From | To (valid) |
|------|------|------------|
| scaffold | INITIALIZED | CLARIFICATION |
| scaffold | CLARIFICATION | ANALYSIS |
| update | INITIALIZED | ANALYSIS |
| both | ANALYSIS | SYNTHESIS |
| both | SYNTHESIS | VALIDATION |
| both | VALIDATION | COMPLETED |

---

## Entry Point

### entry.py

Creates new or loads existing session and triggers agent flow:

```bash
# Scaffold mode (auto-detected if no CLAUDE.md)
python3 entry.py --algorithm-state {alg_id} --target /path/to/project

# Force update mode
python3 entry.py --algorithm-state {alg_id} --target /path/to/project --update

# Resume existing session
python3 entry.py --algorithm-state {alg_id} --scaffold-docs-state {session_id}
```

---

## Language Detection (detector.py)

Auto-detects project language from manifest files:

| Manifest | Language |
|----------|----------|
| `pyproject.toml`, `requirements.txt` | python |
| `package.json` + `tsconfig.json` | typescript |
| `package.json` | javascript |
| `Cargo.toml` | rust |
| `go.mod` | go |
| `pom.xml`, `build.gradle` | java |

Falls back to file extension analysis if no manifest found.

---

## Best Practices Enforced

| Practice | Check |
|----------|-------|
| CLAUDE.md < 100 lines | Validation phase |
| YAML frontmatter in rules | Validation phase |
| No code snippets | Analysis phase |
| file:line references | Synthesis phase |

---

## Agent Memory Files

Each agent creates a memory file:

```
.claude/memory/{session_id}-{agent}-memory.md
```

Example for scaffold mode:
- `abc123-clarification-memory.md`
- `abc123-analysis-memory.md`
- `abc123-synthesis-memory.md`
- `abc123-validation-memory.md`

---

## Tests

Located at: `tests/unit/orchestration/skills/scaffold_docs/`

- `test_scaffold_docs_state.py` - Phase, FSM, State tests
- `test_detector.py` - Language detection tests
- `test_language_defaults.py` - Language defaults tests
- `test_flows.py` - Flow definition tests

Run tests:

```bash
cd .claude/orchestration
source .venv/bin/activate
pytest tests/unit/orchestration/skills/scaffold_docs/ -v
```

---

*Last updated: 2026-01-31*
