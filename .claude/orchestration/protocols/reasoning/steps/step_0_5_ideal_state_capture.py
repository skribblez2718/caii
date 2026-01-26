"""
step_0_5_ideal_state_capture.py
================================

Step 0.5 of the Mandatory Reasoning Protocol: IDEAL STATE Capture

This step implements "The Last Algorithm" methodology by iteratively refining
explicit success criteria, anti-criteria, and verification methods until
95% completeness is achieved (or max 5 iterations).

Key Features:
- Fully dynamic clarification cycles (0-5 based on need)
- Exit immediately when IDEAL STATE >= 95% complete
- No mandatory cycles - avoids over-reasoning
- Max 5 cycles as hard limit

The IDEAL STATE captures:
- SUCCESS CRITERIA: What must be true for success (measurable, verifiable)
- ANTI-CRITERIA: What must be avoided (things that would constitute failure)
- SUCCESS METRICS: Quantifiable measures of success
- EXIT CONDITION: How we know the task is complete

Reference: The Last Algorithm - "Verifiability is the universal ladder"
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
from reasoning.config.config import (
    STEPS_DIR,
    format_mandatory_directive,
)


class Step05IdealStateCapture(BaseStep):
    """
    Step 0.5: IDEAL STATE Capture with iterative clarification.

    Captures explicit success criteria through dynamic clarification cycles.
    Exits when completeness >= 95% or max 5 iterations reached.

    The IDEAL STATE is passed to all downstream steps and agents,
    providing clear verification criteria for task completion.
    """
    _step_num = 0.5
    _step_name = "IDEAL_STATE_CAPTURE"

    # Configuration constants
    MAX_ITERATIONS = 5
    MIN_COMPLETENESS = 0.95  # 95% threshold

    def get_extra_context(self) -> str:
        """
        Provide Johari findings and current IDEAL STATE iteration context.
        """
        # Get iteration info
        iteration = self.state.ideal_state_iteration + 1
        max_iter = self.MAX_ITERATIONS

        context_parts = []

        # Show iteration context
        context_parts.append(
            f"## IDEAL STATE Capture - Iteration {iteration}/{max_iter}\n"
        )

        # Show Johari findings from Step 0 if available
        johari_output = self.state.step_outputs.get(0, {})
        if johari_output:
            context_parts.append("### Johari Window Findings (from Step 0)")
            schema = johari_output.get("johari_schema", {})
            if schema:
                context_parts.append(f"- **Open:** {schema.get('open', 'N/A')}")
                context_parts.append(f"- **Blind:** {schema.get('blind', 'N/A')}")
                context_parts.append(f"- **Hidden:** {schema.get('hidden', 'N/A')}")
                context_parts.append(f"- **Unknown:** {schema.get('unknown', 'N/A')}")
            context_parts.append("")

        # Show current IDEAL STATE if exists (from previous iteration)
        if self.state.ideal_state:
            completeness = self.state.get_ideal_state_completeness()
            context_parts.append(f"### Current IDEAL STATE (Iteration {self.state.ideal_state_iteration})")
            context_parts.append(f"- **Completeness:** {completeness:.0%}")

            # Show existing criteria counts
            sc_count = len(self.state.ideal_state.get("success_criteria", []))
            ac_count = len(self.state.ideal_state.get("anti_criteria", []))
            sm_count = len(self.state.ideal_state.get("success_metrics", []))
            context_parts.append(f"- **Success Criteria:** {sc_count}")
            context_parts.append(f"- **Anti-Criteria:** {ac_count}")
            context_parts.append(f"- **Success Metrics:** {sm_count}")

            # Show sufficiency assessment
            sufficiency = self.state.ideal_state.get("sufficiency", {})
            if sufficiency:
                gaps = sufficiency.get("gaps", [])
                if gaps:
                    context_parts.append(f"- **Gaps to Address:** {', '.join(gaps)}")
            context_parts.append("")

        # Show user query for reference
        context_parts.append("### User Query")
        context_parts.append(f"```\n{self.state.user_query}\n```\n")

        return "\n".join(context_parts)

    def process_step(self) -> dict:
        """
        Return metadata about IDEAL STATE capture expectations.

        The actual IDEAL STATE definition is performed by Claude following
        the markdown instructions. This method documents the expected structure
        that Claude should produce.

        Returns:
            Dict with IDEAL STATE schema and instructions for Claude
        """
        return {
            "ideal_state_schema": {
                "success_criteria": [
                    {
                        "id": "SC-N",
                        "criterion": "Description of what must be true",
                        "verifiable": True,
                        "verification_method": "How to verify this criterion",
                        "priority": "must-have | should-have | nice-to-have",
                    }
                ],
                "anti_criteria": [
                    {
                        "id": "AC-N",
                        "criterion": "Description of what must be avoided",
                        "verifiable": True,
                        "verification_method": "How to verify absence",
                    }
                ],
                "success_metrics": [
                    {
                        "id": "SM-N",
                        "name": "Metric name",
                        "target_value": "Target value or range",
                        "measurement_method": "How to measure",
                    }
                ],
                "completeness_score": "0.0-1.0 (95% = sufficient)",
                "exit_condition": {
                    "description": "When task is considered complete",
                    "minimum_completeness": 0.95,
                },
                "sufficiency": {
                    "is_sufficient": "True if completeness >= 95%",
                    "confidence": "high | medium | low",
                    "gaps": ["List of gaps if not sufficient"],
                },
            },
            "iteration": self.state.ideal_state_iteration + 1,
            "max_iterations": self.MAX_ITERATIONS,
            "min_completeness": self.MIN_COMPLETENESS,
        }

    def print_next_directive(self) -> None:
        """
        Conditional directive based on IDEAL STATE sufficiency.

        Three possible outcomes:
        1. IDEAL STATE >= 95% complete → Proceed to Step 1
        2. IDEAL STATE < 95% AND can iterate → Loop back to Step 0.5
        3. Max iterations reached → Proceed to Step 1 (with warning)
        """
        from reasoning.config.config import ORCHESTRATION_ROOT

        # Get current state
        can_iterate = self.state.can_iterate_ideal_state()
        is_sufficient = self.state.is_ideal_state_sufficient()
        iteration = self.state.ideal_state_iteration
        completeness = self.state.get_ideal_state_completeness()

        # Build directive based on state
        step1_script = STEPS_DIR / "step_1_semantic_understanding.py"
        step05_script = STEPS_DIR / "step_0_5_ideal_state_capture.py"

        print("## IDEAL STATE Assessment")
        print()

        if is_sufficient:
            # Sufficient completeness OR max iterations - proceed to Step 1
            if iteration >= self.MAX_ITERATIONS:
                print(f"**Max iterations ({self.MAX_ITERATIONS}) reached.** Proceeding with current IDEAL STATE.")
            else:
                print(f"**IDEAL STATE sufficient ({completeness:.0%} completeness).** Proceeding to Step 1.")
            print()
            directive = format_mandatory_directive(
                f"python3 {step1_script} --state {self.state.state_file_path}",
                "IDEAL STATE captured. Execute Step 1 (Semantic Understanding)."
            )
            print(directive)
        else:
            # Insufficient - provide options
            print(f"**IDEAL STATE incomplete ({completeness:.0%} < 95%).**")
            print()
            print("### Decision Options")
            print()
            print("**Option 1: Ask for Clarification** (Recommended if gaps exist)")
            print("- Use AskUserQuestion tool to gather missing information")
            print("- Then execute Step 0.5 again to refine IDEAL STATE")
            print()

            if can_iterate:
                print(f"**Option 2: Iterate** (Cycle {iteration + 1}/{self.MAX_ITERATIONS})")
                print(f"- Refine criteria based on current understanding")
                print(f"- Command: `python3 {step05_script} --state {self.state.state_file_path}`")
                print()

            print("**Option 3: Proceed Anyway** (Use with caution)")
            print("- Accept current IDEAL STATE despite gaps")
            directive = format_mandatory_directive(
                f"python3 {step1_script} --state {self.state.state_file_path}",
                "Proceed to Step 1 despite incomplete IDEAL STATE."
            )
            print(f"- {directive}")


# Allow running as script
if __name__ == "__main__":
    sys.exit(Step05IdealStateCapture.main())
