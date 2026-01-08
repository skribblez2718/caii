"""develop-learnings Completion - includes memory cleanup after learnings captured"""
import subprocess
import sys
from pathlib import Path

_MEMORY_DIR = Path(__file__).resolve().parents[4] / "memory"

def cleanup_memory_files() -> int:
    """Remove all memory files after learnings have been captured."""
    if not _MEMORY_DIR.exists():
        return 0
    try:
        count_result = subprocess.run(f'find {_MEMORY_DIR} -name "*.md" -type f | wc -l',
            shell=True, capture_output=True, text=True, timeout=10)
        count = int(count_result.stdout.strip()) if count_result.returncode == 0 else 0
        subprocess.run(f'find {_MEMORY_DIR} -name "*.md" -type f -delete',
            shell=True, capture_output=True, timeout=30)
        return count
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
        return 0

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from skill.composite.common_skill_complete import skill_complete
    skill_complete(Path(__file__).parent.name.replace("_", "-"))
    cleaned = cleanup_memory_files()
    if cleaned > 0:
        print(f"**CLEANUP:** {cleaned} memory files removed")
