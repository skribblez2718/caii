"""
Verification Entry Point (Step 8)

Verifies output against IDEAL STATE criteria.
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace

from orchestration.entry_base import PhaseConfig, run_phase_entry

# Step number for this phase (preserved for backward compatibility)
STEP_NUM = 8


def _verify_extra_placeholders(state: Any) -> Dict[str, Any]:
    """Extra placeholders for VERIFY phase (backward compatibility)."""
    return {"task_id": state.session_id}


if __name__ == "__main__":
    run_phase_entry(
        __file__,
        PhaseConfig(
            step_num=8,
            phase_name="VERIFY",
            content_file="verification.md",
            description="VERIFY Phase (Step 8)",
            extra_placeholders=_verify_extra_placeholders,
        ),
    )
