"""
step_0_johari_discovery.py
==========================

Step 0 of the Mandatory Reasoning Protocol: Johari Window Discovery

This pre-step executes at the START of every interaction to transform
unknown unknowns into known knowns using the SHARE/ASK/ACKNOWLEDGE/EXPLORE
framework before formal reasoning begins.

After Step 0, the protocol routes to Step 0.5 (IDEAL STATE Capture) for
explicit success criteria definition before proceeding to Step 1.
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
from reasoning.config.config import STEPS_DIR, format_mandatory_directive


class Step0JohariDiscovery(BaseStep):
    """
    Step 0: Johari Window Discovery

    Systematically explores unknown unknowns before formal reasoning.
    Uses SHARE/ASK/ACKNOWLEDGE/EXPLORE framework to surface ambiguities.

    The Johari findings from this step are used downstream when invoking agents.
    The DA should extract and pass these findings to build_agent_prompt().
    """
    _step_num = 0
    _step_name = "JOHARI_DISCOVERY"

    def get_extra_context(self) -> str:
        """
        Step 0 is the first step, so provides context about the user query.
        """
        return f"{self.state.user_query}\n"

    def process_step(self) -> dict:
        """
        Return structured metadata for Johari findings.

        The actual Johari analysis is performed by Claude following the
        markdown instructions. This method documents the expected structure
        that the DA should extract from Claude's analysis.

        The DA uses these findings when invoking agents via build_agent_prompt()
        to provide prior knowledge context.

        Returns:
            Dict with Johari structure metadata
        """
        return {
            "johari_schema": {
                "open": "Confirmed knowledge, verified facts, shared understanding",
                "blind": "Identified gaps, missing context, unknown requirements",
                "hidden": "Inferences, assumptions, non-obvious insights",
                "unknown": "Edge cases, potential risks, areas for exploration",
            },
            "usage": "DA extracts Johari findings from Step 0 analysis and passes to agents",
            "downstream": "build_agent_prompt() accepts johari_findings parameter",
        }

    def print_next_directive(self) -> None:
        """
        Route to Step 0.5 (IDEAL STATE Capture) instead of Step 1.

        Step 0.5 captures explicit success criteria, anti-criteria, and
        verification methods using "The Last Algorithm" methodology.
        """
        step_0_5_script = STEPS_DIR / "step_0_5_ideal_state_capture.py"
        directive = format_mandatory_directive(
            f"python3 {step_0_5_script} --state {self.state.state_file_path}",
            "Johari Discovery complete. Execute Step 0.5 (IDEAL STATE Capture)."
        )
        print(directive)


# Allow running as script
if __name__ == "__main__":
    sys.exit(Step0JohariDiscovery.main())
