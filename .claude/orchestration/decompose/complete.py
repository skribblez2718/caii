"""
DECOMPOSE Protocol Completion Handler

Handles subtask creation, routing, and aggregation triggering:
- complete_decomposition(): Create subtask states and route first ready subtask
- on_subtask_complete(): Handle subtask completion and route next
- trigger_aggregation(): Start aggregation flow when all subtasks done
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from orchestration.decompose.flows import AGGREGATION_FLOW
from orchestration.flow_invoker import invoke_agent_flow
from orchestration.state.algorithm_state import AlgorithmState

# Content directory for decompose protocol
CONTENT_DIR = Path(__file__).parent / "content"


def complete_decomposition(
    parent_state: AlgorithmState,
    subtasks: List[Dict[str, Any]],
) -> str:
    """
    Create subtask states and route first ready subtask to GATHER.

    This is called after DECOMPOSE_FLOW validation step completes with GO verdict.
    Creates AlgorithmState for each subtask, registers them in parent, and
    returns directive to route the first ready subtask to GATHER.

    Args:
        parent_state: The parent AlgorithmState (complex/very_complex task)
        subtasks: List of subtask dicts from synthesis agent output, each with:
            - subtask_id: Unique identifier (e.g., "ST-001")
            - description: Subtask description
            - complexity: Should be "simple" (enforced by synthesis)
            - dependencies: List of subtask_ids this depends on

    Returns:
        Directive string to route first ready subtask to GATHER phase

    Critical Invariant:
        State is ALWAYS saved before returning directive.
    """
    # Map subtask_id to actual session_id for dependency resolution
    id_mapping: Dict[str, str] = {}

    # Create AlgorithmState for each subtask
    for idx, subtask_def in enumerate(subtasks):
        subtask_state = AlgorithmState(
            user_query=subtask_def["description"],
            complexity=subtask_def.get("complexity", "simple"),
            parent_task_id=parent_state.session_id,
            subtask_index=idx,
        )
        subtask_state.save()

        # Map original subtask_id to actual session_id
        id_mapping[subtask_def["subtask_id"]] = subtask_state.session_id

    # Register subtasks in parent with resolved dependencies
    for subtask_def in subtasks:
        subtask_session_id = id_mapping[subtask_def["subtask_id"]]

        # Resolve dependency IDs to session IDs
        dep_ids = subtask_def.get("dependencies", [])
        resolved_deps = [id_mapping[dep_id] for dep_id in dep_ids if dep_id in id_mapping]

        parent_state.register_subtask(subtask_session_id, resolved_deps)

    # CRITICAL: Save state BEFORE returning directive
    parent_state.save()

    # Get first ready subtask
    ready_subtasks = parent_state.get_ready_subtasks()
    if not ready_subtasks:
        return "ERROR: No ready subtasks after decomposition. Check dependencies for cycles."

    first_subtask_id = ready_subtasks[0]

    # Return directive to route to GATHER
    return _build_gather_directive(first_subtask_id)


def on_subtask_complete(state: AlgorithmState) -> Optional[str]:
    """
    Handle subtask completion after LEARN phase.

    Called when a subtask completes its full algorithm cycle (LEARN phase).
    Updates parent state and determines next action:
    - If more subtasks ready: return GATHER directive for next
    - If all subtasks complete: return aggregation directive
    - If not a subtask: return None

    Args:
        state: The AlgorithmState of the completed subtask

    Returns:
        Directive string for next action, or None if not a subtask
    """
    # Check if this is a subtask
    if not state.is_subtask:
        return None

    # Load parent state
    parent_state = AlgorithmState.load(state.parent_task_id)
    if parent_state is None:
        return f"ERROR: Parent state {state.parent_task_id} not found"

    # Mark this subtask as complete in parent
    parent_state.mark_subtask_complete(state.session_id)
    parent_state.save()

    # Check if all subtasks are complete
    if parent_state.all_subtasks_complete():
        return trigger_aggregation(parent_state)

    # Get next ready subtasks
    ready_subtasks = parent_state.get_ready_subtasks()
    if not ready_subtasks:
        # No ready subtasks but not all complete - waiting on dependencies
        return (
            "WAITING: No subtasks ready. "
            "Waiting for dependent subtasks to complete."
        )

    # Route next ready subtask to GATHER
    next_subtask_id = ready_subtasks[0]
    return _build_gather_directive(next_subtask_id)


def trigger_aggregation(parent_state: AlgorithmState) -> str:
    """
    Start AGGREGATION_FLOW to combine subtask results.

    Called when all subtasks are complete. Invokes the aggregation flow
    which uses the synthesis agent to combine outputs.

    Args:
        parent_state: The parent AlgorithmState with all subtasks complete

    Returns:
        Directive string for AGGREGATION_FLOW invocation
    """
    return invoke_agent_flow(
        flow=AGGREGATION_FLOW,
        task_id=parent_state.session_id,
        skill_name="decompose",
        phase_id="aggregation",
        domain="technical",
        task_description="Aggregate subtask results into final deliverable",
        skill_content_dir=CONTENT_DIR,
    )


def _build_gather_directive(subtask_id: str) -> str:
    """
    Build directive to route subtask to GATHER phase.

    Args:
        subtask_id: Session ID of the subtask

    Returns:
        Directive string for GATHER invocation
    """
    return f"""## Route Subtask to GATHER

**Subtask ID:** `{subtask_id}`

Execute the GATHER phase for this subtask:

```bash
python3 ${{CAII_DIRECTORY}}/.claude/orchestration/outer_loop/gather/entry.py --state {subtask_id}
```

The subtask will proceed through the full algorithm:
GATHER → IDEAL → OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
"""
