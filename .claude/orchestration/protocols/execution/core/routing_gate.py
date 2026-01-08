"""Routing Gate - Task Triviality Validation for Agent Enforcement

This module implements the routing gate pattern that validates whether tasks
qualify as "trivial" and can proceed with direct tool usage, or whether they
require cognitive agent invocation for proper execution.

The gate enforces a fail-secure design: when ANY trivial criterion is not met,
the system defaults to requiring agent invocation rather than allowing direct
tool usage.

Note: Skill routing is now handled semantically through the reasoning protocol's
Step 3b (skill detection) and Step 4 (task routing), not by keyword matching.
Penny's semantic understanding from DA.md provides robust skill selection.

Philosophy Alignment:
- PRINCIPLE 2: Orchestration-Implementation Separation
  - Gate makes orchestration decisions (WHETHER to use agents)
  - Does not implement task execution logic (HOW to do work)
- PRINCIPLE 6: Embedded Validation Over Separate Phases
  - Validation integrated at decision point within existing protocols
  - Not a separate validation phase

Usage:
    from core.routing_gate import RoutingGate, GateDecision

    gate = RoutingGate()
    decision = gate.validate_triviality("Fix typo in README line 42")

    if decision == GateDecision.TRIVIAL_APPROVED:
        # Proceed with direct tool usage
        pass
    elif decision == GateDecision.AGENT_REQUIRED:
        # Invoke appropriate agent with memory protocol
        pass
    elif decision == GateDecision.CLARIFICATION_NEEDED:
        # Invoke clarification-agent for ambiguous tasks
        pass
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class TrivialCriteria:
    """Five criteria that ALL must be true for task to qualify as trivial.

    Conservative bias: if uncertain about any criterion, mark as False
    to default to agent invocation (fail-secure design).

    Attributes:
        single_file: Task affects only one file (no multi-file changes)
        five_lines_or_less: Task changes 5 lines or fewer
        mechanical_operation: Task is purely mechanical (typo/rename/delete)
        no_research_needed: Task requires no information gathering
        no_decisions_needed: Task requires no judgment calls
    """
    single_file: bool
    five_lines_or_less: bool
    mechanical_operation: bool
    no_research_needed: bool
    no_decisions_needed: bool

    def all_met(self) -> bool:
        """Return True only if ALL 5 criteria are True.

        This enforces the ALL-must-be-true logic required for trivial
        task approval. Even one False criterion means task is non-trivial.

        Returns:
            bool: True if all criteria met, False if any criterion fails
        """
        return all([
            self.single_file,
            self.five_lines_or_less,
            self.mechanical_operation,
            self.no_research_needed,
            self.no_decisions_needed
        ])


class GateDecision(Enum):
    """Routing gate decision outcomes.

    TRIVIAL_APPROVED: All 5 trivial criteria met, direct tool usage allowed
    AGENT_REQUIRED: One or more criteria failed, agent invocation mandatory
    CLARIFICATION_NEEDED: Criteria cannot be evaluated, invoke clarification-agent

    Note: Skill routing is handled semantically in the reasoning protocol
    (Step 3b + Step 4), not in the routing gate.
    """
    TRIVIAL_APPROVED = "trivial_approved"
    AGENT_REQUIRED = "agent_required"
    CLARIFICATION_NEEDED = "clarification_needed"


class RoutingGate:
    """Validates task triviality using LLM-based self-assessment.

    This gate uses structured prompts to guide Penny through explicit
    evaluation of all 5 trivial criteria, then parses the yes/no responses
    to make a routing decision.

    Note: Skill routing is handled semantically by the reasoning protocol
    (Step 3b skill detection + Step 4 task routing), not by this gate.

    Design Pattern: GUARD - validates preconditions before execution
    Failure Mode: Fail-secure - ambiguity defaults to agent invocation
    """

    # Prompt template for self-assessment with few-shot examples
    ASSESSMENT_PROMPT_TEMPLATE = """=== TRIVIAL TASK GATE: MANDATORY SELF-ASSESSMENT ===

TASK TO EVALUATE: {task_description}

YOU MUST evaluate this task against ALL 5 trivial criteria below.

RESPOND IN EXACTLY THIS FORMAT (copy and complete):

CRITERION 1 - SINGLE_FILE: [YES/NO]
CRITERION 2 - FIVE_LINES_OR_LESS: [YES/NO]
CRITERION 3 - MECHANICAL_OPERATION: [YES/NO]
CRITERION 4 - NO_RESEARCH_NEEDED: [YES/NO]
CRITERION 5 - NO_DECISIONS_NEEDED: [YES/NO]

=== CRITERION DEFINITIONS ===

1. SINGLE_FILE: Does this task affect ONLY ONE file? (YES = one file, NO = multiple files or uncertain)
2. FIVE_LINES_OR_LESS: Will this task change 5 lines or fewer? (YES = 5 or less, NO = more than 5 or uncertain)
3. MECHANICAL_OPERATION: Is this PURELY mechanical (typo fix, simple rename, delete unused)? (YES = purely mechanical, NO = requires any reasoning)
4. NO_RESEARCH_NEEDED: Can this be done with NO information gathering? (YES = no research, NO = needs any lookup)
5. NO_DECISIONS_NEEDED: Does this require ZERO judgment calls? (YES = zero judgment, NO = any decision needed)

=== FEW-SHOT EXAMPLES ===

EXAMPLE 1 - TRIVIAL TASK:
Task: "Fix typo 'recieve' to 'receive' in README.md line 42"

CRITERION 1 - SINGLE_FILE: YES
CRITERION 2 - FIVE_LINES_OR_LESS: YES
CRITERION 3 - MECHANICAL_OPERATION: YES
CRITERION 4 - NO_RESEARCH_NEEDED: YES
CRITERION 5 - NO_DECISIONS_NEEDED: YES

Result: ALL YES -> Task is TRIVIAL -> Direct tool usage allowed

EXAMPLE 2 - NON-TRIVIAL TASK:
Task: "Refactor the authentication module to use JWT"

CRITERION 1 - SINGLE_FILE: NO
CRITERION 2 - FIVE_LINES_OR_LESS: NO
CRITERION 3 - MECHANICAL_OPERATION: NO
CRITERION 4 - NO_RESEARCH_NEEDED: NO
CRITERION 5 - NO_DECISIONS_NEEDED: NO

Result: ANY NO -> Task is NON-TRIVIAL -> Agent invocation required

EXAMPLE 3 - BORDERLINE (defaults to non-trivial):
Task: "Update the error message in login.py"

CRITERION 1 - SINGLE_FILE: YES
CRITERION 2 - FIVE_LINES_OR_LESS: YES
CRITERION 3 - MECHANICAL_OPERATION: NO
CRITERION 4 - NO_RESEARCH_NEEDED: YES
CRITERION 5 - NO_DECISIONS_NEEDED: NO

Result: TWO NO -> Task is NON-TRIVIAL -> Agent invocation required

=== STRICT INSTRUCTIONS ===

1. You MUST respond with the EXACT format shown above
2. Use ONLY "YES" or "NO" - no other values (not "yes", "maybe", "probably")
3. If UNCERTAIN about ANY criterion, answer NO (conservative/fail-secure)
4. Do NOT include explanations within the criteria block
5. Your response MUST contain the 5 CRITERION lines with [YES/NO] replaced

NOW EVALUATE THE TASK AND RESPOND:"""

    # Retry prompt for when initial parsing fails
    RETRY_PROMPT_TEMPLATE = """Your previous response could not be parsed correctly.

Please respond EXACTLY in this format with NO explanations:

CRITERION 1 - SINGLE_FILE: YES or NO
CRITERION 2 - FIVE_LINES_OR_LESS: YES or NO
CRITERION 3 - MECHANICAL_OPERATION: YES or NO
CRITERION 4 - NO_RESEARCH_NEEDED: YES or NO
CRITERION 5 - NO_DECISIONS_NEEDED: YES or NO

Replace "YES or NO" with your actual answer. Use UPPERCASE YES or NO only."""

    @staticmethod
    def generate_assessment_prompt(task_description: str) -> str:
        """Generate structured self-assessment prompt for task triviality.

        Args:
            task_description: Clear description of the task to evaluate

        Returns:
            str: Formatted prompt with task description injected

        Example:
            >>> gate = RoutingGate()
            >>> prompt = gate.generate_assessment_prompt("Fix typo in README line 42")
            >>> print(prompt)
            TRIVIAL TASK SELF-ASSESSMENT

            Task: Fix typo in README line 42

            Evaluate ALL 5 criteria below...
        """
        return RoutingGate.ASSESSMENT_PROMPT_TEMPLATE.format(
            task_description=task_description
        )

    @staticmethod
    def validate_response_structure(response: str) -> tuple:
        """Validate response contains expected structure before parsing.

        Pre-validation ensures all 5 criterion markers are present and each
        has a YES/NO answer. This catches malformed responses early.

        Args:
            response: The raw response to validate

        Returns:
            tuple: (is_valid: bool, issues: list[str])
                - is_valid: True if structure is valid
                - issues: List of structural issues found
        """
        issues = []

        # Expected criterion markers
        expected_markers = [
            ("CRITERION 1", "SINGLE_FILE"),
            ("CRITERION 2", "FIVE_LINES_OR_LESS"),
            ("CRITERION 3", "MECHANICAL_OPERATION"),
            ("CRITERION 4", "NO_RESEARCH_NEEDED"),
            ("CRITERION 5", "NO_DECISIONS_NEEDED"),
        ]

        response_upper = response.upper()

        for criterion_num, criterion_name in expected_markers:
            # Check if criterion marker exists (flexible matching)
            marker_found = (
                criterion_num in response_upper or
                criterion_name in response_upper or
                f"{criterion_num[10]} - {criterion_name}" in response_upper or  # "1 - SINGLE_FILE"
                f"{criterion_num[10]}." in response_upper  # "1."
            )

            if not marker_found:
                issues.append(f"Missing criterion: {criterion_num} - {criterion_name}")
                continue

            # Find the line containing this criterion and check for YES/NO
            for line in response.split('\n'):
                line_upper = line.upper()
                if criterion_name in line_upper or (criterion_num in line_upper and criterion_name.split('_')[0] in line_upper):
                    if 'YES' not in line_upper and 'NO' not in line_upper:
                        issues.append(f"{criterion_num}: Missing YES/NO answer")
                    break

        return (len(issues) == 0, issues)

    @staticmethod
    def parse_assessment_response(response: str) -> TrivialCriteria:
        """Extract yes/no answers from self-assessment response.

        Uses a robust multi-pattern approach with fallback patterns for each
        criterion. Pre-validates structure before parsing.

        Conservative parsing: if answer is unclear or missing, defaults to False
        (fail-secure behavior - when in doubt, require agent).

        Args:
            response: Penny's response containing YES/NO answers

        Returns:
            TrivialCriteria: Dataclass with boolean values for each criterion

        Raises:
            ValueError: If response cannot be parsed (missing expected structure)

        Example:
            >>> response = '''
            ... CRITERION 1 - SINGLE_FILE: YES
            ... CRITERION 2 - FIVE_LINES_OR_LESS: YES
            ... CRITERION 3 - MECHANICAL_OPERATION: YES
            ... CRITERION 4 - NO_RESEARCH_NEEDED: YES
            ... CRITERION 5 - NO_DECISIONS_NEEDED: NO
            ... '''
            >>> criteria = RoutingGate.parse_assessment_response(response)
            >>> criteria.all_met()
            False
        """
        # Phase 1: Structure validation
        is_valid, issues = RoutingGate.validate_response_structure(response)
        if not is_valid:
            raise ValueError(
                f"Response structure invalid: {', '.join(issues)}"
            )

        # Phase 2: Extract values with robust patterns (multiple fallbacks per criterion)
        patterns = {
            'single_file': [
                r'CRITERION\s*1\s*-\s*SINGLE_FILE\s*:\s*(YES|NO)',
                r'SINGLE_FILE\s*:\s*(YES|NO)',
                r'1\s*[-\.]\s*SINGLE[_\s]*FILE\s*:\s*(YES|NO)',
                r'1\.\s*.*?:\s*(YES|NO)',
            ],
            'five_lines_or_less': [
                r'CRITERION\s*2\s*-\s*FIVE_LINES_OR_LESS\s*:\s*(YES|NO)',
                r'FIVE_LINES_OR_LESS\s*:\s*(YES|NO)',
                r'2\s*[-\.]\s*FIVE[_\s]*LINES\s*:\s*(YES|NO)',
                r'2\.\s*.*?:\s*(YES|NO)',
            ],
            'mechanical_operation': [
                r'CRITERION\s*3\s*-\s*MECHANICAL_OPERATION\s*:\s*(YES|NO)',
                r'MECHANICAL_OPERATION\s*:\s*(YES|NO)',
                r'3\s*[-\.]\s*MECHANICAL\s*:\s*(YES|NO)',
                r'3\.\s*.*?:\s*(YES|NO)',
            ],
            'no_research_needed': [
                r'CRITERION\s*4\s*-\s*NO_RESEARCH_NEEDED\s*:\s*(YES|NO)',
                r'NO_RESEARCH_NEEDED\s*:\s*(YES|NO)',
                r'4\s*[-\.]\s*NO[_\s]*RESEARCH\s*:\s*(YES|NO)',
                r'4\.\s*.*?:\s*(YES|NO)',
            ],
            'no_decisions_needed': [
                r'CRITERION\s*5\s*-\s*NO_DECISIONS_NEEDED\s*:\s*(YES|NO)',
                r'NO_DECISIONS_NEEDED\s*:\s*(YES|NO)',
                r'5\s*[-\.]\s*NO[_\s]*DECISIONS\s*:\s*(YES|NO)',
                r'5\.\s*.*?:\s*(YES|NO)',
            ],
        }

        criteria_values = {}
        parse_warnings = []

        for criterion_name, pattern_list in patterns.items():
            found = False
            for pattern in pattern_list:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    answer = match.group(1).upper()
                    criteria_values[criterion_name] = (answer == 'YES')
                    found = True
                    break

            if not found:
                parse_warnings.append(criterion_name)
                # Fail-secure: if we can't parse, assume NO (requires agent)
                criteria_values[criterion_name] = False

        if parse_warnings:
            # Log warning but don't fail - fail-secure defaults applied
            import sys
            print(f"WARNING: Could not parse criteria: {parse_warnings}. "
                  f"Defaulting to False (fail-secure).", file=sys.stderr)

        return TrivialCriteria(**criteria_values)

    @staticmethod
    def validate_triviality(
        task_description: str,
        llm_response: str,
        context: Optional[dict] = None
    ) -> tuple:
        """Validate task triviality from LLM self-assessment response.

        This is the main entry point for routing gate validation. Takes the
        LLM's response to the assessment prompt and returns a decision.

        Args:
            task_description: Description of the task being evaluated
            llm_response: Penny's response to the assessment prompt
            context: Optional additional context

        Returns:
            tuple: (GateDecision, TrivialCriteria, reason_string)
                - GateDecision: The routing decision
                - TrivialCriteria: Parsed criteria (may have defaults if parse failed)
                - reason_string: Human-readable explanation

        Example:
            >>> prompt = RoutingGate.generate_assessment_prompt("Fix typo")
            >>> response = get_llm_response(prompt)  # Implementation-specific
            >>> decision, criteria, reason = RoutingGate.validate_triviality(
            ...     "Fix typo", response
            ... )
            >>> if decision == GateDecision.TRIVIAL_APPROVED:
            ...     # Proceed with direct tools
            ...     pass
        """
        try:
            criteria = RoutingGate.parse_assessment_response(llm_response)

            if criteria.all_met():
                return (
                    GateDecision.TRIVIAL_APPROVED,
                    criteria,
                    "All 5 trivial criteria met. Direct tool usage approved."
                )
            else:
                # Build explanation of which criteria failed
                failed = []
                if not criteria.single_file:
                    failed.append("SINGLE_FILE")
                if not criteria.five_lines_or_less:
                    failed.append("FIVE_LINES_OR_LESS")
                if not criteria.mechanical_operation:
                    failed.append("MECHANICAL_OPERATION")
                if not criteria.no_research_needed:
                    failed.append("NO_RESEARCH_NEEDED")
                if not criteria.no_decisions_needed:
                    failed.append("NO_DECISIONS_NEEDED")

                return (
                    GateDecision.AGENT_REQUIRED,
                    criteria,
                    f"Criteria failed: {', '.join(failed)}. Agent invocation required."
                )

        except ValueError as e:
            # Parse failure - check if this warrants clarification or fail-secure
            error_msg = str(e)

            # If response indicates genuine uncertainty/confusion
            uncertainty_markers = ['unclear', 'uncertain', 'need more', "can't determine"]
            if any(marker in llm_response.lower() for marker in uncertainty_markers):
                return (
                    GateDecision.CLARIFICATION_NEEDED,
                    TrivialCriteria(False, False, False, False, False),
                    f"Response indicates uncertainty. Clarification needed. Error: {error_msg}"
                )

            # Otherwise, fail-secure to agent requirement
            return (
                GateDecision.AGENT_REQUIRED,
                TrivialCriteria(False, False, False, False, False),
                f"Could not parse response (fail-secure). Error: {error_msg}"
            )


class RoutingGateWorkflow:
    """Orchestrates the complete routing gate workflow with retry logic.

    This class provides a higher-level interface that manages the full
    gate workflow including:
    - Initial assessment prompt generation
    - Response validation
    - Retry on parse failure
    - Fail-secure defaults

    Note: Skill routing is handled by the reasoning protocol (Step 3b + Step 4),
    not by the routing gate workflow.

    Design Pattern: WORKFLOW - coordinates multiple steps with recovery
    """

    MAX_RETRIES = 1

    @classmethod
    def execute_gate(
        cls,
        task_description: str,
        get_llm_response: callable,
        context: Optional[dict] = None
    ) -> tuple:
        """Execute the complete gate workflow with retry logic.

        Args:
            task_description: The task to evaluate
            get_llm_response: Callable that takes prompt string and returns LLM response
            context: Optional additional context

        Returns:
            tuple: (GateDecision, TrivialCriteria, reason_string)

        Example:
            >>> def get_response(prompt):
            ...     # Your LLM call implementation
            ...     return llm.generate(prompt)
            >>> decision, criteria, reason = RoutingGateWorkflow.execute_gate(
            ...     "fix typo in README",
            ...     get_response
            ... )
            >>> if decision == GateDecision.TRIVIAL_APPROVED:
            ...     print("Direct tool usage allowed")
        """
        prompt = RoutingGate.generate_assessment_prompt(task_description)

        for attempt in range(cls.MAX_RETRIES + 1):
            # Get LLM response
            response = get_llm_response(prompt)

            # Validate structure first
            is_valid, issues = RoutingGate.validate_response_structure(response)

            if is_valid:
                # Structure valid - proceed with full validation
                return RoutingGate.validate_triviality(
                    task_description, response, context
                )

            # Structure invalid - retry with clarification prompt if retries remain
            if attempt < cls.MAX_RETRIES:
                prompt = RoutingGate.RETRY_PROMPT_TEMPLATE
                continue

            # Max retries exhausted - fail-secure
            return (
                GateDecision.AGENT_REQUIRED,
                TrivialCriteria(False, False, False, False, False),
                f"Parse failed after {cls.MAX_RETRIES + 1} attempts. "
                f"Issues: {', '.join(issues)}. Defaulting to agent required."
            )

        # Should not reach here, but fail-secure just in case
        return (
            GateDecision.AGENT_REQUIRED,
            TrivialCriteria(False, False, False, False, False),
            "Unexpected workflow state. Defaulting to agent required."
        )


# Module-level convenience functions
def assess_task_triviality(task_description: str) -> str:
    """Generate self-assessment prompt for task triviality evaluation.

    Convenience function for quick access to routing gate assessment prompt.

    Args:
        task_description: Description of task to evaluate

    Returns:
        str: Formatted self-assessment prompt for Penny

    Example:
        >>> prompt = assess_task_triviality("Update version in package.json")
        >>> # Present prompt to Penny for self-assessment
    """
    return RoutingGate.generate_assessment_prompt(task_description)
