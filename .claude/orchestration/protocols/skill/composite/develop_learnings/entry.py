"""develop-learnings Entry Point"""
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add protocols directory to path for skill imports
    entry_path = Path(__file__).resolve()
    sys.path.insert(0, str(entry_path.parents[3]))

    # Add .claude directory to path for orchestration module import
    sys.path.insert(0, str(entry_path.parents[5]))

    from orchestration import LEARNINGS_DIR
    from skill.composite.common_skill_entry import skill_entry

    # Ensure learnings directories exist before skill execution
    COGNITIVE_FUNCTIONS = ['clarification', 'research', 'analysis', 'synthesis', 'generation', 'validation', 'memory']
    for function in COGNITIVE_FUNCTIONS:
        dir_path = LEARNINGS_DIR / function
        dir_path.mkdir(parents=True, exist_ok=True)

    skill_entry(entry_path.parent.name.replace("_", "-"), entry_path.parent)
