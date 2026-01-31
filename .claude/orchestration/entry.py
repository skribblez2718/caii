"""
Global Orchestration Entry Point

Routes user prompts based on DA's complexity assessment.
Python enforces sequence; DA makes decisions.

Flow:
1. Print complexity analysis prompt for DA
2. DA determines complexity classification
3. DA executes routing command with --complexity argument
4. Python routes based on complexity:
   - trivial -> DA handles directly
   - simple/moderate -> The Last Algorithm (GATHER)
   - complex/very_complex -> DECOMPOSE protocol
"""

import argparse
from pathlib import Path

from orchestration.state import AlgorithmState
from orchestration.utils import load_content, substitute_placeholders


def print_complexity_prompt(user_query: str) -> None:
    """Print prompt for DA to assess complexity."""
    content = load_content(__file__, "complexity_assessment.md")
    entry_path = Path(__file__).resolve()
    prompt = substitute_placeholders(
        content, user_query=user_query, entry_path=str(entry_path)
    )
    print(prompt)


def extract_complexity(response: str) -> str:
    """
    Extract complexity classification from LLM response.

    Supports 5 METR categories in priority order:
    very_complex > complex > moderate > simple > trivial > unknown

    Handles case-insensitive matching and hyphen/space/underscore variants.

    Returns: 'trivial', 'simple', 'moderate', 'complex', 'very_complex', or 'unknown'
    """
    # Normalize: lowercase, replace hyphens and underscores with spaces
    response_lower = response.lower().replace("-", " ").replace("_", " ")

    # Priority-ordered matching (most restrictive first)
    if "very complex" in response_lower:
        return "very_complex"
    if "complex" in response_lower:
        return "complex"
    if "moderate" in response_lower:
        return "moderate"
    if "simple" in response_lower:
        return "simple"
    if "trivial" in response_lower:
        return "trivial"
    return "unknown"


def route_based_on_complexity(response: str, user_query: str) -> None:
    """Route to appropriate execution path based on DA's complexity assessment.

    Routing logic for 5 METR categories:
    - trivial: DA direct execution (no state)
    - simple/moderate: The Last Algorithm via GATHER phase
    - complex/very_complex: DECOMPOSE protocol (task decomposition)
    """
    complexity = extract_complexity(response)

    if complexity == "trivial":
        # No state, DA handles directly
        print("\n## Route: DA Direct Execution")
        print("Task classified as TRIVIAL. Proceeding without The Last Algorithm.")
        print(f"\n**Task:** {user_query}")
        print("\nExecute the task directly.")

    elif complexity in ("simple", "moderate"):
        # Create state and route to GATHER
        state = AlgorithmState.for_task(user_query, complexity=complexity)
        state.save()  # CRITICAL: Save BEFORE directive

        gather_entry = Path(__file__).parent / "outer_loop" / "gather" / "entry.py"

        print(f"\n## Route: The Last Algorithm ({complexity.upper()})")
        print(f"Session: {state.session_id}")

        directive = f"""
**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**

```bash
python3 {gather_entry} --state {state.session_id}
```

**Context:** Execute GATHER phase before proceeding.

**Warnings:**
- Execute this command NOW. Do NOT respond with text first.
- FAILURE to execute breaks the system's reliability guarantee.
"""
        print(directive)

    elif complexity in ("complex", "very_complex"):
        # Create state and route to DECOMPOSE protocol
        state = AlgorithmState.for_task(user_query, complexity=complexity)
        state.save()  # CRITICAL: Save BEFORE directive

        decompose_entry = Path(__file__).parent / "decompose" / "entry.py"

        complexity_display = complexity.upper().replace("_", " ")
        print(f"\n## Route: DECOMPOSE Protocol ({complexity_display})")
        print(f"Session: {state.session_id}")
        print("\nTask requires decomposition before proceeding to GATHER.")

        directive = f"""
**MANDATORY - EXECUTE IMMEDIATELY BEFORE ANY OTHER ACTION:**

```bash
python3 {decompose_entry} --state {state.session_id}
```

**Context:** Execute DECOMPOSE phase to break task into smaller subtasks.

**Warnings:**
- Execute this command NOW. Do NOT respond with text first.
- FAILURE to execute breaks the system's reliability guarantee.
"""
        print(directive)

    else:
        # Unknown defaults to moderate (safe)
        print("\n## WARNING: Could not determine complexity")
        print(f"Response was: '{response[:200]}'")
        print("Defaulting to MODERATE for safety.")
        route_based_on_complexity("moderate", user_query)


def main() -> None:
    """Entry point: either print complexity prompt or route based on classification."""
    parser = argparse.ArgumentParser(
        description="Global orchestration entry point for complexity-based routing"
    )
    parser.add_argument(
        "user_query",
        help="The user's task/query to process",
    )
    parser.add_argument(
        "--complexity",
        choices=["trivial", "simple", "moderate", "complex", "very_complex"],
        help="Complexity classification from DA (triggers routing)",
    )

    args = parser.parse_args()

    if args.complexity:
        # DA's decision triggers routing
        route_based_on_complexity(args.complexity, args.user_query)
    else:
        # Initial call - print assessment prompt
        print_complexity_prompt(args.user_query)


if __name__ == "__main__":
    main()
