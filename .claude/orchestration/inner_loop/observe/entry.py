"""
OBSERVE Phase Entry Point (Step 1)

Semantic understanding of the task.
"""

import sys
from pathlib import Path

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

from orchestration.entry_base import PhaseConfig, run_phase_entry

# Step number for this phase (preserved for backward compatibility)
STEP_NUM = 1

if __name__ == "__main__":
    run_phase_entry(
        __file__,
        PhaseConfig(
            step_num=1,
            phase_name="OBSERVE",
            content_file="observe_phase.md",
            description="OBSERVE Phase (Step 1)",
        ),
    )
