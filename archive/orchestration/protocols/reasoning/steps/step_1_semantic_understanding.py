"""
step_1_semantic_understanding.py
================================

Step 1 of the Mandatory Reasoning Protocol: Semantic Understanding

This step interprets the semantic meaning behind the user's query,
identifies the task domain, and determines the appropriate approach.

Step 1 receives IDEAL STATE context from Step 0.5, which provides
explicit success criteria to guide semantic interpretation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Path setup - add protocols directory for fully-qualified imports
# This prevents collision between reasoning/config and skill/config
_STEPS_DIR = Path(__file__).resolve().parent
_REASONING_ROOT = _STEPS_DIR.parent
_PROTOCOLS_DIR = _REASONING_ROOT.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

from reasoning.steps.base import BaseStep


class Step1SemanticUnderstanding(BaseStep):
    """
    Step 1: Semantic Understanding

    Interprets query intent, identifies task domain, and determines approach.
    Uses IDEAL STATE from Step 0.5 to guide interpretation.
    """
    _step_num = 1
    _step_name = "SEMANTIC_UNDERSTANDING"

    def get_extra_context(self) -> str:
        """
        Provide IDEAL STATE context from Step 0.5 to guide semantic understanding.
        """
        context_parts = []

        # Get IDEAL STATE from protocol state
        ideal_state = self.state.ideal_state
        if ideal_state:
            context_parts.append("## IDEAL STATE Context (from Step 0.5)")
            context_parts.append("")

            # Success criteria count
            sc_count = len(ideal_state.get("success_criteria", []))
            ac_count = len(ideal_state.get("anti_criteria", []))
            sm_count = len(ideal_state.get("success_metrics", []))

            context_parts.append(f"- **Success Criteria:** {sc_count} defined")
            context_parts.append(f"- **Anti-Criteria:** {ac_count} defined")
            context_parts.append(f"- **Success Metrics:** {sm_count} defined")

            # Exit condition
            exit_cond = ideal_state.get("exit_condition", {})
            if exit_cond:
                context_parts.append(f"- **Exit Condition:** {exit_cond.get('description', 'Not specified')}")

            # Completeness
            completeness = ideal_state.get("completeness_score", 0)
            context_parts.append(f"- **Completeness:** {completeness:.0%}")

            context_parts.append("")
            context_parts.append("Use the IDEAL STATE to guide your semantic interpretation.")
            context_parts.append("The success criteria define what 'success' looks like for this task.")
            context_parts.append("")

        return "\n".join(context_parts)


# Allow running as script
if __name__ == "__main__":
    sys.exit(Step1SemanticUnderstanding.main())
