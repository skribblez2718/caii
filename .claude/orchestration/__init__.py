"""
CAII Orchestration Package

Python-based orchestration implementing The Last Algorithm.
"""

from orchestration.utils import (
    get_content_dir,
    load_content,
    substitute_placeholders,
)
from orchestration.entry import main as orchestration_main

# State module exports
from orchestration.state import (
    SESSIONS_DIR,
    SCHEMA_VERSION,
    generate_session_id,
    BaseFSM,
    BaseState,
    AlgorithmPhase,
    AlgorithmFSM,
    AlgorithmState,
)

__all__ = [
    # Utilities
    "get_content_dir",
    "load_content",
    "substitute_placeholders",
    # Entry point
    "orchestration_main",
    # State module
    "SESSIONS_DIR",
    "SCHEMA_VERSION",
    "generate_session_id",
    "BaseFSM",
    "BaseState",
    "AlgorithmPhase",
    "AlgorithmFSM",
    "AlgorithmState",
]
