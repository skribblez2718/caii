"""
IDEAL STATE Verification Module
===============================

Builds verification directives from IDEAL STATE data for post-execution
cognitive verification.

This module creates MANDATORY directives that force Claude to explicitly
verify each success criterion, anti-criterion, and success metric before
a skill can be marked as complete.

Key Principle: Cognitive verification, NOT automated checks.
Claude must explicitly read, understand, and confirm/deny each criterion.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Path setup - add protocols directory for fully-qualified imports
_VERIFIER_DIR = Path(__file__).resolve().parent
_PROTOCOLS_DIR = _VERIFIER_DIR.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))


def build_verification_directive(
    skill_state: Any,  # SkillExecutionState
    reasoning_state: Any,  # ProtocolState
) -> str:
    """
    Build MANDATORY verification directive with all IDEAL STATE criteria.

    Args:
        skill_state: The skill execution state
        reasoning_state: The reasoning protocol state containing IDEAL STATE

    Returns:
        Formatted verification directive string
    """
    ideal_state = reasoning_state.ideal_state
    if not ideal_state:
        return ""

    # Build context info
    context = {
        "task_id": skill_state.task_id,
        "skill_name": skill_state.skill_name,
        "session_id": skill_state.session_id,
        "user_query": getattr(reasoning_state, "user_query", "N/A"),
    }

    # Build the verification checklist
    checklist = _build_verification_checklist(ideal_state)

    # Format with enforcement language
    return _format_verification_enforcement(checklist, context)


def _build_verification_checklist(ideal_state: Dict[str, Any]) -> str:
    """
    Generate structured checklist from IDEAL STATE components.

    Args:
        ideal_state: The IDEAL STATE dictionary

    Returns:
        Markdown-formatted verification checklist
    """
    sections = []

    # Success Criteria
    success_criteria = ideal_state.get("success_criteria", [])
    if success_criteria:
        sections.append(_format_success_criteria_section(success_criteria))

    # Anti-Criteria
    anti_criteria = ideal_state.get("anti_criteria", [])
    if anti_criteria:
        sections.append(_format_anti_criteria_section(anti_criteria))

    # Success Metrics
    success_metrics = ideal_state.get("success_metrics", [])
    if success_metrics:
        sections.append(_format_success_metrics_section(success_metrics))

    # Exit Condition
    exit_condition = ideal_state.get("exit_condition", {})
    if exit_condition:
        sections.append(_format_exit_condition_section(exit_condition))

    return "\n\n".join(sections)


def _format_success_criteria_section(criteria: List[Dict[str, Any]]) -> str:
    """Format success criteria as verification table."""
    header = """## SUCCESS CRITERIA VERIFICATION (MUST ALL BE TRUE)

For each criterion below, you MUST explicitly state: VERIFIED or NOT VERIFIED

| ID | Priority | Criterion | Verification Method | Your Verification |
|----|----------|-----------|---------------------|-------------------|"""

    rows = []
    for i, c in enumerate(criteria, 1):
        criterion_id = c.get("id", f"SC-{i}")
        priority = c.get("priority", "must-have")
        criterion = c.get("criterion", "Unknown criterion")
        method = c.get("verification_method", "Manual verification")
        rows.append(f"| {criterion_id} | {priority} | {criterion} | {method} | [ ] VERIFIED / NOT VERIFIED |")

    return header + "\n" + "\n".join(rows)


def _format_anti_criteria_section(criteria: List[Dict[str, Any]]) -> str:
    """Format anti-criteria as verification table."""
    header = """## ANTI-CRITERIA VERIFICATION (MUST NOT BE VIOLATED)

For each anti-criterion below, confirm it was NOT violated:

| ID | Anti-Criterion | Verification Method | Your Verification |
|----|----------------|---------------------|-------------------|"""

    rows = []
    for i, c in enumerate(criteria, 1):
        criterion_id = c.get("id", f"AC-{i}")
        criterion = c.get("criterion", "Unknown anti-criterion")
        method = c.get("verification_method", "Manual verification")
        rows.append(f"| {criterion_id} | {criterion} | {method} | [ ] NOT VIOLATED / VIOLATED |")

    return header + "\n" + "\n".join(rows)


def _format_success_metrics_section(metrics: List[Dict[str, Any]]) -> str:
    """Format success metrics as assessment table."""
    header = """## SUCCESS METRICS ASSESSMENT

| ID | Metric | Target Value | Measurement | Achieved? |
|----|--------|--------------|-------------|-----------|"""

    rows = []
    for i, m in enumerate(metrics, 1):
        metric_id = m.get("id", f"SM-{i}")
        name = m.get("name", "Unknown metric")
        target = m.get("target_value", "N/A")
        method = m.get("measurement_method", "Manual measurement")
        rows.append(f"| {metric_id} | {name} | {target} | {method} | [ ] YES / NO / PARTIAL |")

    return header + "\n" + "\n".join(rows)


def _format_exit_condition_section(exit_condition: Dict[str, Any]) -> str:
    """Format exit condition verification."""
    description = exit_condition.get("description", "Task completion criteria not specified")
    min_completeness = exit_condition.get("minimum_completeness", 0.95)

    return f"""## EXIT CONDITION

**Defined Exit Condition:** {description}
**Minimum Completeness Required:** {min_completeness * 100:.0f}%
**Your Assessment:** [ ] EXIT CONDITION MET / NOT MET"""


def _format_verification_enforcement(checklist: str, context: Dict[str, Any]) -> str:
    """
    Format with VERY STRONG enforcement language.

    Args:
        checklist: The verification checklist content
        context: Context information (task_id, skill_name, etc.)

    Returns:
        Full verification directive with enforcement language
    """
    task_id = context.get("task_id", "unknown")
    skill_name = context.get("skill_name", "unknown")
    user_query = context.get("user_query", "N/A")

    # Truncate user query if too long
    if len(user_query) > 200:
        user_query = user_query[:200] + "..."

    directive = f"""
================================================================================
  ABSOLUTE MANDATORY - IDEAL STATE VERIFICATION - NON-NEGOTIABLE
================================================================================

**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**

You MUST cognitively verify the IDEAL STATE criteria defined at reasoning Step 0.5.

**Task Context:**
- Task ID: `{task_id}`
- Skill: `{skill_name}`
- Original Request: {user_query}

{checklist}

---

## VERIFICATION SUMMARY (REQUIRED)

You MUST complete this summary BEFORE skill completion proceeds:

**All must-have criteria verified:** [ ] YES / NO
**No anti-criteria violated:** [ ] YES / NO
**Exit condition met:** [ ] YES / NO
**Overall verification:** [ ] PASS / FAIL

---

**IF VERIFICATION PASSES:** Continue with skill completion. State: "IDEAL STATE VERIFICATION: PASS"
**IF VERIFICATION FAILS:** HALT and explain which criteria failed. State: "IDEAL STATE VERIFICATION: FAIL - [reason]"

================================================================================
WARNINGS:
- ABSOLUTE: You MUST verify EACH criterion above BEFORE skill completion.
- NON-NEGOTIABLE: Skill completion is BLOCKED until you explicitly confirm ALL verifications.
- CRITICAL: Do NOT skip any criterion. Do NOT assume verification. CONFIRM explicitly.
- FAILURE to complete this verification invalidates the entire skill execution.
================================================================================
"""
    return directive.strip()


def has_ideal_state(reasoning_state: Any) -> bool:
    """
    Check if the reasoning state has an IDEAL STATE defined.

    Args:
        reasoning_state: The reasoning protocol state

    Returns:
        True if IDEAL STATE exists and has content
    """
    if not reasoning_state:
        return False

    ideal_state = getattr(reasoning_state, "ideal_state", None)
    if not ideal_state:
        return False

    # Check if it has any meaningful content
    has_criteria = bool(ideal_state.get("success_criteria"))
    has_anti = bool(ideal_state.get("anti_criteria"))
    has_metrics = bool(ideal_state.get("success_metrics"))

    return has_criteria or has_anti or has_metrics
