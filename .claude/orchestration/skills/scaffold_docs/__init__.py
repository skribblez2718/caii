"""
scaffold-docs Skill

Initialize and maintain project documentation following best practices.
Creates CLAUDE.md, .claude/rules/, and docs/ directory.
"""

from orchestration.skills.scaffold_docs.scaffold_docs_state import (
    ScaffoldDocsPhase,
    ScaffoldDocsFSM,
    ScaffoldDocsState,
)
from orchestration.skills.scaffold_docs.flows import (
    SCAFFOLD_FLOW,
    UPDATE_FLOW,
    get_flow_for_mode,
)
from orchestration.skills.scaffold_docs.detector import (
    detect_language,
    LanguageInfo,
)
from orchestration.skills.scaffold_docs.language_defaults import (
    get_language_defaults,
    LanguageDefaults,
)

__all__ = [
    "ScaffoldDocsPhase",
    "ScaffoldDocsFSM",
    "ScaffoldDocsState",
    "SCAFFOLD_FLOW",
    "UPDATE_FLOW",
    "get_flow_for_mode",
    "detect_language",
    "LanguageInfo",
    "get_language_defaults",
    "LanguageDefaults",
]
