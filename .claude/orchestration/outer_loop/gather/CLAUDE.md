# GATHER Phase (Step 0)

## Purpose

Dynamic state gathering based on task domain classification.
Implements the Johari Window Protocol for domain-aware state collection.

## Flow

```
GATHER → INTERVIEW → [Inner Loop] → VERIFY
  │
  ├── 1. Load algorithm state
  ├── 2. Classify task domain
  ├── 3. Trigger research → analysis agent flow
  └── 4. Agents gather domain-specific state information
```

## Files

| File | Purpose |
|------|---------|
| `entry.py` | Phase entry point |
| `flows.py` | Agent flow definitions (GATHER_FLOW) |
| `domain_classifier.py` | Task domain classification |
| `content/gather/research.md` | Research agent instructions |
| `content/gather/analysis.md` | Analysis agent instructions |

## Agent Flow

The GATHER phase uses a research → analysis agent chain:

1. **Research Agent**: Gathers domain-specific current state
2. **Analysis Agent**: Structures findings for downstream phases

## Domain Classification

Supports 11 task domains:
- CODING, CORRESPONDENCE, RESEARCH, DOCUMENT
- SOCIAL, CREATIVE, PERSONAL, PROFESSIONAL
- TECHNICAL_OPS, DATA, GENERAL

## Entry Point

```bash
python3 entry.py --state <session_id>
```

Options:
- `--state`: Required. Algorithm session ID
- `--no-flow`: Skip agent flow (legacy mode)
