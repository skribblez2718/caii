"""Inner Loop - OBSERVE → THINK → PLAN → BUILD → EXECUTE → LEARN."""

# Phase entry points exposed for import
# Note: These are entry point modules, not functions
# Use: from orchestration.inner_loop import observe_entry; observe_entry.main()
from orchestration.inner_loop.observe import entry as observe_entry
from orchestration.inner_loop.think import entry as think_entry
from orchestration.inner_loop.plan import entry as plan_entry
from orchestration.inner_loop.build import entry as build_entry
from orchestration.inner_loop.execute import entry as execute_entry
from orchestration.inner_loop.learn import entry as learn_entry

__all__ = [
    "observe_entry",
    "think_entry",
    "plan_entry",
    "build_entry",
    "execute_entry",
    "learn_entry",
]
