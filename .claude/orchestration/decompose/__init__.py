"""
Decompose Protocol

Breaks complex/very_complex tasks into SIMPLE subtasks.
Each subtask proceeds through the full algorithm (GATHER → ... → LEARN).
Results are aggregated via AGGREGATION_FLOW.
"""

from orchestration.decompose.flows import AGGREGATION_FLOW, DECOMPOSE_FLOW
from orchestration.decompose.complete import (
    complete_decomposition,
    on_subtask_complete,
    trigger_aggregation,
)

__all__ = [
    "DECOMPOSE_FLOW",
    "AGGREGATION_FLOW",
    "complete_decomposition",
    "on_subtask_complete",
    "trigger_aggregation",
]
