"""
Flow Registry - Central registry of all agent flows.

Enables flow lookup by ID for continuation logic.
All skills and protocols register their flows here.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.agent_chain.flow import AgentFlow

# Registry populated lazily to avoid circular imports
_FLOW_REGISTRY: Dict[str, "AgentFlow"] = {}
_INITIALIZED: bool = False


def _init_registry() -> None:
    """Initialize registry with all known flows (lazy load)."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    # Import flows here to avoid circular imports at module load
    from orchestration.skills.perform_tdd.flows import TDD_PHASE_FLOWS
    from orchestration.decompose.flows import DECOMPOSE_FLOW, AGGREGATION_FLOW

    # Register TDD flows
    for flow in TDD_PHASE_FLOWS.values():
        _FLOW_REGISTRY[flow.flow_id] = flow

    # Register decompose flows
    _FLOW_REGISTRY[DECOMPOSE_FLOW.flow_id] = DECOMPOSE_FLOW
    _FLOW_REGISTRY[AGGREGATION_FLOW.flow_id] = AGGREGATION_FLOW

    # Future: Add more flows here as needed
    # from orchestration.skills.scaffold_docs.flows import ...
    # from orchestration.outer_loop.verify.flows import ...

    _INITIALIZED = True


def register_flow(flow: "AgentFlow") -> None:
    """
    Register a flow by its ID.

    This allows dynamic registration of flows at runtime,
    e.g., for custom or dynamic flows.

    Args:
        flow: AgentFlow to register
    """
    _init_registry()  # Ensure base flows are loaded
    _FLOW_REGISTRY[flow.flow_id] = flow


def get_flow(flow_id: str) -> Optional["AgentFlow"]:
    """
    Look up a flow by ID.

    Args:
        flow_id: The flow ID to look up (e.g., "perform-tdd-red")

    Returns:
        AgentFlow if found, None otherwise
    """
    _init_registry()  # Ensure initialized
    return _FLOW_REGISTRY.get(flow_id)


def list_flows() -> List[str]:
    """
    List all registered flow IDs.

    Returns:
        List of all flow IDs in the registry
    """
    _init_registry()
    return list(_FLOW_REGISTRY.keys())
