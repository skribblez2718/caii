# Johari Window Protocol

## ABSOLUTE MANDATE

Execute BEFORE any substantive work. No assumptions. No implied requirements.

## Quadrants

| Quadrant | Definition | AI Perspective | Action |
|----------|------------|----------------|--------|
| **OPEN** | Known to both | Confirmed facts | Document |
| **BLIND** | Known to user only | User's assumptions | PROBE |
| **HIDDEN** | Known to AI only | Technical context | SHARE |
| **UNKNOWN** | Unknown to both | Edge cases | EXPLORE |

## SHARE (Hidden → Open)

What you know that user may not:
- Technical implications and risks
- Alternative approaches
- Common pitfalls
- Critical design decisions

## PROBE (Blind → Open)

What user knows that you don't:
- Specific intent and goals
- Constraints and preferences
- Domain knowledge
- Success criteria

## MAP (Unknown → Known)

Collective blind spots:
- Edge cases not discussed
- Unexamined assumptions
- Unconsidered failure modes

## DELIVER

If ANY ambiguity exists:

1. HALT - Do not proceed
2. INVOKE `AskUserQuestion` tool with max 5 questions
3. WAIT for response

**Priority Levels:**
- **P0:** Blocking - cannot proceed
- **P1:** Important - affects approach
- **P2:** Clarifying - can assume default

## FORBIDDEN

- "No ambiguities detected - proceeding"
- "Assuming standard interpretation"
- Proceeding with any unresolved ambiguity
