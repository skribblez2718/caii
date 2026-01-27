"""Outer Loop - GATHER → IDEAL STATE → [Inner Loop] → VERIFY."""

# Phase entry points exposed for import
# Note: These are entry point modules, not functions
# Use: from orchestration.outer_loop import gather_entry; gather_entry.main()
from orchestration.outer_loop.gather import entry as gather_entry
from orchestration.outer_loop.ideal_state import entry as ideal_state_entry
from orchestration.outer_loop.verify import entry as verify_entry

__all__ = [
    "gather_entry",
    "ideal_state_entry",
    "verify_entry",
]
