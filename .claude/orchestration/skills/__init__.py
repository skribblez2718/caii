"""Skills Module - Composite cognitive workflows.

Skills are invoked by path, not imported directly.
This module provides namespace organization.
"""

# Skills are invoked via their entry points:
#   python3 skills/tdd/entry.py --algorithm-state {id}
#
# For programmatic access to skill modules:
#   from orchestration.skills.tdd import TDDState, TDDPhase

__all__ = []
