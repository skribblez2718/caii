"""
step_3b_skill_detection.py
==========================

Step 3b of the Mandatory Reasoning Protocol: Semantic Skill Detection

This step runs AFTER Step 3 (Tree of Thought) and BEFORE Step 4 (Task Routing).
It presents available skills to the orchestrator for SEMANTIC evaluation based on the
"When to Use" patterns defined in DA.md.

NO KEYWORD MATCHING is used. The orchestrator makes the skill detection decision based on
semantic understanding of the user's query and the skill descriptions.

Agent Mode Routing:
- Normal sessions: Step 3b → Step 4 (Task Routing)
- Agent mode sessions: Step 3b → Step 5 (Self-Consistency) - agents are already routed
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Path setup - add protocols directory for fully-qualified imports
# This prevents collision between reasoning/config and skill/config
_STEPS_DIR = Path(__file__).resolve().parent
_REASONING_ROOT = _STEPS_DIR.parent
_PROTOCOLS_DIR = _REASONING_ROOT.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

from reasoning.steps.base import BaseStep


# Available skills for semantic matching
# These descriptions are used by the orchestrator to semantically determine skill applicability
COMPOSITE_SKILLS = {
    "develop-skill": {
        "description": "Meta-skill for creating/updating workflow skills and system modifications",
        "when_to_use": [
            "New workflow pattern or orchestration capability needed",
            "Existing skill needs enhancement or modification",
            "ANY system modifications (skills, agents, protocols, architecture)",
            "Meta-work on workflows themselves",
        ],
        "examples": [
            "Create a skill for code review workflows",
            "Update develop-skill to include new phases",
            "Modify the routing system",
            "Update agent protocols",
        ],
    },
    "develop-learnings": {
        "description": "Transform workflow experiences into structured, reusable learnings",
        "when_to_use": [
            "Post-workflow capture of insights needed",
            "Resolved unknowns should become permanent knowledge",
            "Pattern or anti-pattern worth preserving discovered",
            "Agent improvement based on discoveries needed",
        ],
        "examples": [
            "Capture what we learned from this project",
            "Document this approach for future use",
            "Remember not to do this again",
        ],
    },
}

ATOMIC_SKILLS = {
    "orchestrate-clarification": {
        "description": "Transform vague inputs into actionable specifications",
        "when_to_use": ["Ambiguity must be resolved before cognitive work can proceed"],
    },
    "orchestrate-research": {
        "description": "Investigate options and gather domain knowledge",
        "when_to_use": ["Knowledge gaps must be filled before design decisions"],
    },
    "orchestrate-analysis": {
        "description": "Decompose complex problems and map dependencies",
        "when_to_use": ["Complexity needs systematic decomposition"],
    },
    "orchestrate-synthesis": {
        "description": "Integrate findings into coherent designs",
        "when_to_use": ["Multiple inputs need integration into coherent whole"],
    },
    "orchestrate-generation": {
        "description": "Generate artifacts using TDD methodology",
        "when_to_use": ["Specifications are ready for artifact creation"],
    },
    "orchestrate-validation": {
        "description": "Verify artifacts against quality criteria",
        "when_to_use": ["Quality verification required before completion"],
    },
}


class Step3bSkillDetection(BaseStep):
    """
    Step 3b: Semantic Skill Detection

    Presents available skills to the orchestrator for SEMANTIC evaluation.
    No keyword matching - the orchestrator decides based on understanding from DA.md.

    Also handles agent mode routing:
    - Normal sessions proceed to Step 4 (Task Routing)
    - Agent mode sessions skip to Step 5 (Self-Consistency)
    """
    _step_num = 3  # Logically part of step 3
    _step_name = "SKILL_DETECTION"

    def is_agent_mode(self) -> bool:
        """
        Check if running in agent mode.

        In agent mode, Step 4 (Task Routing) is skipped since agents are already routed.

        Returns:
            True if running in agent mode, False otherwise
        """
        return self.state.metadata.get("is_agent_session", False)

    def process_step(self) -> Dict[str, Any]:
        """
        Process skill detection.

        Returns minimal output - the orchestrator makes the semantic decision.
        """
        return {
            "skill_detection_method": "semantic",
            "note": "Orchestrator evaluates skills semantically based on DA.md patterns",
            "completed": True,
        }

    def get_extra_context(self) -> str:
        """
        Present available skills for the orchestrator's semantic evaluation.
        """
        query = getattr(self.state, "user_query", "")

        context_parts = [
            "## Step 3b: Semantic Skill Detection",
            "",
            "Evaluate the user's query against available skills using your semantic understanding",
            "from DA.md. **DO NOT use keyword matching** - use semantic understanding of intent.",
            "",
            f"**User Query:** {query}",
            "",
            "---",
            "",
            "## Available Composite Skills",
            "",
        ]

        for skill_name, skill_info in COMPOSITE_SKILLS.items():
            context_parts.append(f"### {skill_name}")
            context_parts.append(f"**Description:** {skill_info['description']}")
            context_parts.append("")
            context_parts.append("**When to Use:**")
            for condition in skill_info["when_to_use"]:
                context_parts.append(f"- {condition}")
            context_parts.append("")
            context_parts.append("**Examples:**")
            for example in skill_info["examples"]:
                context_parts.append(f"- \"{example}\"")
            context_parts.append("")

        context_parts.extend([
            "---",
            "",
            "## Available Atomic Skills (for dynamic sequencing)",
            "",
        ])

        for skill_name, skill_info in ATOMIC_SKILLS.items():
            context_parts.append(f"- **{skill_name}**: {skill_info['description']}")

        context_parts.extend([
            "",
            "---",
            "",
            "## Your Semantic Evaluation",
            "",
            "Based on the user's query and your understanding of these skill patterns:",
            "",
            "1. **Evaluate semantically** - Does the query's INTENT match a skill's purpose?",
            "2. **Consider context** - What is the user trying to accomplish?",
            "3. **Apply DA.md patterns** - Use the 'When to Use' guidance you received at session start",
            "",
            "**Respond with your detection in this format:**",
            "```",
            "SKILL_DETECTED: [yes|no]",
            "SKILL_NAME: [skill-name or null]",
            "SKILL_TYPE: [composite|atomic|null]",
            "CONFIDENCE: [high|medium|low]",
            "REASONING: [Brief semantic justification]",
            "```",
            "",
        ])

        return "\n".join(context_parts)

    def execute(self) -> bool:
        """
        Execute semantic skill detection step.
        """
        from reasoning.core.fsm import ReasoningState
        from datetime import datetime, timezone

        # Transition to SKILL_DETECTION state
        if not self.state.fsm.transition(ReasoningState.SKILL_DETECTION):
            print(f"ERROR: Cannot transition to SKILL_DETECTION from {self.state.fsm.state}")
            return False

        output = self.process_step()

        # Store in state
        self.state.step_outputs["3b"] = output
        self.state.step_timestamps["3b"] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state.save()

        # Print skill context for semantic evaluation
        context = self.get_extra_context()
        print(context)

        # Route based on agent mode
        if self.is_agent_mode():
            # Agent mode: skip Step 4 (Task Routing) and go directly to Step 5
            self.print_next_step_5_directive()
        else:
            # Normal mode: proceed to Step 4 (Task Routing)
            self.print_next_step_4_directive()

        return True

    def print_next_step_4_directive(self) -> None:
        """Print directive to execute Step 4 (Task Routing)."""
        from reasoning.config.config import STEPS_DIR, format_mandatory_directive

        step_4_script = STEPS_DIR / "step_4_task_routing.py"

        directive = format_mandatory_directive(
            f"python3 {step_4_script} --state {self.state.state_file_path}",
            "Skill detection complete. Execute Step 4 (Task Routing). "
        )
        print(directive)

    def print_next_step_5_directive(self) -> None:
        """Print directive to execute Step 5 (Self-Consistency) for agent mode."""
        from reasoning.config.config import STEPS_DIR, format_mandatory_directive

        step_5_script = STEPS_DIR / "step_5_self_consistency.py"

        directive = format_mandatory_directive(
            f"python3 {step_5_script} --state {self.state.state_file_path}",
            "Agent mode: Step 4 skipped. Execute Step 5 (Self-Consistency). "
        )
        print(directive)

    @classmethod
    def main(cls) -> int:
        """Main entry point for step 3b script."""
        import argparse
        from reasoning.core.state import ProtocolState

        parser = argparse.ArgumentParser(
            description="Execute Step 3b: Semantic Skill Detection",
        )
        parser.add_argument(
            "--state",
            required=True,
            help="Path to the state file"
        )

        args = parser.parse_args()

        state_path = Path(args.state)
        if not state_path.exists():
            print(f"ERROR: State file not found: {args.state}", file=sys.stderr)
            return 1

        session_id = state_path.stem.replace("reasoning-", "")

        state = ProtocolState.load(session_id)
        if not state:
            print(f"ERROR: Could not load state from {args.state}", file=sys.stderr)
            return 1

        step = cls(state)
        if not step.execute():
            return 1

        return 0


if __name__ == "__main__":
    sys.exit(Step3bSkillDetection.main())
