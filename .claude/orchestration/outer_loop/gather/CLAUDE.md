# GATHER Phase (Step 0)

## Purpose

Collect and clarify all requirements before execution begins.

## Agentic Flow

The GATHER phase uses an agentic flow to:
1. Analyze the task requirements
2. Identify ambiguities and unknowns
3. Clarify with user if needed
4. Prepare context for IDEAL STATE capture

## Johari Protocol

The Johari Window protocol is available at:
`.claude/orchestration/johari/`

Agents within the GATHER flow may invoke Johari to:
- Surface unknown unknowns
- Execute SHARE/PROBE/MAP/DELIVER framework
- Trigger user clarification via AskUserQuestion

**Note:** Johari is NOT directly wired to this step.
It is called by agents as needed within the agentic flow.

## Entry Point

`python3 entry.py "<user_query>"`
