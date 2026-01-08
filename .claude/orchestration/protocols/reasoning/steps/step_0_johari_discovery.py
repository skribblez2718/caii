"""
step_0_johari_discovery.py
==========================

Step 0 of the Mandatory Reasoning Protocol: Johari Window Discovery

This pre-step executes at the START of every interaction to transform
unknown unknowns into known knowns using the SHARE/ASK/ACKNOWLEDGE/EXPLORE
framework before formal reasoning begins.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Path setup - add protocols directory for fully-qualified imports
# This prevents collision between reasoning/config and skill/config
_STEPS_DIR = Path(__file__).resolve().parent
_REASONING_ROOT = _STEPS_DIR.parent
_PROTOCOLS_DIR = _REASONING_ROOT.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

from reasoning.steps.base import BaseStep


class Step0JohariDiscovery(BaseStep):
    """
    Step 0: Johari Window Discovery

    Systematically explores unknown unknowns before formal reasoning.
    Uses SHARE/ASK/ACKNOWLEDGE/EXPLORE framework to surface ambiguities.
    """
    _step_num = 0
    _step_name = "JOHARI_DISCOVERY"

    def get_extra_context(self) -> str:
        """
        Step 0 is the first step, so provides context about the user query.
        """
        return f"**User Query:** {self.state.user_query}\n"


# Allow running as script
if __name__ == "__main__":
    sys.exit(Step0JohariDiscovery.main())
