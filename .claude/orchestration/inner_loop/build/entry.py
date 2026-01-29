"""
BUILD Phase Entry Point (Step 4)

Agent orchestration and artifact creation.
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
STEP_NUM = 4

if __name__ == "__main__":
    run_phase_entry(
        __file__,
        PhaseConfig(
            step_num=4,
            phase_name="BUILD",
            content_file="build_phase.md",
            description="BUILD Phase (Step 4)",
        ),
    )
