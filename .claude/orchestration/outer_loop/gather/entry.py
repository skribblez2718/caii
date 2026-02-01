"""
GATHER Phase Entry Point (Step 0)

Dynamic state gathering based on task domain classification.
Domain-aware state collection using the Johari Window Protocol.

Flow:
1. Load algorithm state
2. Classify task domain
3. Trigger research -> analysis agent flow
4. Agents gather domain-specific state information
"""

import argparse
import sys
from pathlib import Path

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

# pylint: disable=wrong-import-position

from orchestration.state import AlgorithmState
from orchestration.state.algorithm_fsm import AlgorithmPhase
from orchestration.agent_chain.orchestrator import ChainOrchestrator
from orchestration.outer_loop.gather.domain_classifier import (
    classify_domain,
    get_domain_description,
    TaskDomain,
)
from orchestration.outer_loop.gather.flows import GATHER_FLOW

# Step number for this phase
STEP_NUM = 0

# Content directory for agent-specific content
CONTENT_DIR = Path(__file__).parent / "content"


def main() -> None:
    """GATHER phase entry point."""
    parser = argparse.ArgumentParser(description="GATHER Phase (Step 0)")
    parser.add_argument(
        "--state",
        required=True,
        help="Algorithm session ID",
    )
    parser.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip agent flow (legacy mode - just print info)",
    )
    args = parser.parse_args()

    # Load algorithm state
    state = AlgorithmState.load(args.state)
    if not state:
        print(f"ERROR: Session {args.state} not found", file=sys.stderr)
        sys.exit(1)

    # Classify domain if not already set
    if not state.task_domain:
        domain, confidence = classify_domain(state.user_query)
        state.task_domain = domain.value
        state.metadata["domain_confidence"] = confidence
        state.metadata["domain_classification_method"] = "keyword"

    # Transition to GATHER phase
    if state.current_phase == AlgorithmPhase.INITIALIZED:
        if not state.start_phase(AlgorithmPhase.GATHER):
            print("ERROR: Cannot transition to GATHER phase", file=sys.stderr)
            sys.exit(1)

    # CRITICAL: Save state BEFORE printing directive
    state.save()

    # Print phase header
    print("## GATHER Phase (Step 0)")
    print()
    print(f"**Session:** {state.session_id}")
    print(f"**Task:** {state.user_query[:100]}...")
    domain_desc = get_domain_description_safe(state.task_domain)
    print(f"**Domain:** {state.task_domain.upper()} ({domain_desc})")
    print()

    # Legacy mode: just print info
    if args.no_flow:
        print("### State Gathering Requirements")
        print()
        print(f"Domain: {state.task_domain}")
        print(f"Query: {state.user_query}")
        print()
        print("In legacy mode - agent flow not triggered.")
        return

    # Agent flow mode: trigger the research -> analysis chain
    task_description = f"Gather current state for {state.task_domain} task"

    # Create orchestrator
    orchestrator = ChainOrchestrator(
        flow=GATHER_FLOW,
        task_id=state.session_id,
        skill_content_dir=CONTENT_DIR,
        skill_name="outer-loop",
        phase_id="gather",
        domain=state.task_domain,
        task_description=task_description,
    )

    # Print flow info
    print("---")
    print()
    print(f"**Flow:** {GATHER_FLOW.name} (`{GATHER_FLOW.flow_id}`)")
    print(f"**Agents:** {' → '.join(s.agent_name for s in GATHER_FLOW.steps)}")
    print()

    # Start the flow
    directive = orchestrator.start_flow()
    print(directive)


def get_domain_description_safe(domain_value: str) -> str:
    """Get domain description safely from string value."""
    try:
        domain = TaskDomain(domain_value.lower())
        return get_domain_description(domain)
    except ValueError:
        return "Unknown domain"


if __name__ == "__main__":
    main()
