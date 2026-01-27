# Johari Window Protocol

Standalone protocol for transforming unknown unknowns into known knowns.

## Purpose

Called by agents (within GATHER or other phases) to surface ambiguities
and clarify requirements before proceeding.

## Entry Point

`python3 entry.py "<user_query>"`

## Framework: SHARE/PROBE/MAP/DELIVER

1. **SHARE:** What AI knows that user may not
2. **PROBE:** What user knows that AI doesn't
3. **MAP:** Surface collective blind spots
4. **DELIVER:** Targeted questions (max 5)

## HALT-AND-ASK Rule

If ANY ambiguity exists:
1. STOP
2. INVOKE AskUserQuestion tool
3. WAIT for response
4. ONLY THEN proceed
