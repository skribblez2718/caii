"""
Pytest Configuration and Fixtures
=================================

Provides shared fixtures for all test modules:
- Temporary directories for state and memory files
- Mock task_id and session_id generation
- State file creation helpers
- Memory file creation helpers
- AlgorithmFSM and AlgorithmState fixtures
- Cleanup utilities

Usage in tests:
    def test_something(temp_state_dir, mock_task_id):
        # temp_state_dir is a Path to a temporary directory
        # mock_task_id is a unique task ID for this test
        pass
"""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest

# Bootstrap: Add .claude directory to path for orchestration imports
_p = Path(__file__).resolve()
while _p.name != "orchestration" and _p != _p.parent:
    _p = _p.parent
if _p.name == "orchestration" and str(_p.parent) not in sys.path:
    sys.path.insert(0, str(_p.parent))
del _p  # Clean up namespace


# ==============================================================================
# Directory Fixtures
# ==============================================================================


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory that's cleaned up after test."""
    yield tmp_path


@pytest.fixture
def temp_state_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary state directory for session states."""
    state_dir = tmp_path / "sessions"
    state_dir.mkdir(parents=True, exist_ok=True)
    yield state_dir


@pytest.fixture
def temp_memory_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary memory directory for agent memory files."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    yield memory_dir


@pytest.fixture
def temp_orchestration_dirs(tmp_path: Path) -> Generator[Dict[str, Path], None, None]:
    """
    Provide a complete temporary orchestration directory structure.

    Returns dict with:
        - root: Orchestration root
        - sessions: Session state files directory
        - memory: Memory files directory
    """
    dirs = {
        "root": tmp_path,
        "sessions": tmp_path / "state" / "sessions",
        "memory": tmp_path / "memory",
    }

    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    yield dirs


# ==============================================================================
# ID Generation Fixtures
# ==============================================================================


@pytest.fixture
def mock_task_id() -> str:
    """Generate a unique task ID for testing (16 char format)."""
    return f"test-{uuid.uuid4().hex[:12]}"


@pytest.fixture
def mock_session_id() -> str:
    """Generate a 12-char session ID matching production format."""
    return uuid.uuid4().hex[:12]


@pytest.fixture
def mock_ids() -> Dict[str, str]:
    """Generate a complete set of mock IDs for a workflow."""
    return {
        "task_id": f"test-{uuid.uuid4().hex[:12]}",
        "session_id": uuid.uuid4().hex[:12],
    }


# ==============================================================================
# AlgorithmFSM Fixtures
# ==============================================================================


@pytest.fixture
def algorithm_fsm():
    """
    Provide a fresh AlgorithmFSM instance.

    Usage:
        def test_fsm_transition(algorithm_fsm):
            from orchestration.state.algorithm_fsm import AlgorithmPhase
            assert algorithm_fsm.transition(AlgorithmPhase.GATHER)
    """
    from orchestration.state.algorithm_fsm import AlgorithmFSM

    return AlgorithmFSM()


@pytest.fixture
def algorithm_fsm_at_phase():
    """
    Factory fixture to create AlgorithmFSM at specific phase.

    Usage:
        def test_verify_loopback(algorithm_fsm_at_phase):
            from orchestration.state.algorithm_fsm import AlgorithmPhase
            fsm = algorithm_fsm_at_phase(AlgorithmPhase.VERIFY)
            assert fsm.state == AlgorithmPhase.VERIFY
    """
    from orchestration.state.algorithm_fsm import AlgorithmFSM, AlgorithmPhase

    def _create(phase: AlgorithmPhase) -> AlgorithmFSM:
        fsm = AlgorithmFSM(initial_state=phase)
        return fsm

    return _create


# ==============================================================================
# AlgorithmState Fixtures
# ==============================================================================


@pytest.fixture
def create_algorithm_state(temp_state_dir: Path, monkeypatch):
    """
    Factory fixture to create AlgorithmState instances with temp directory.

    Usage:
        state = create_algorithm_state(user_query="Build an API")
    """
    from orchestration.state import config as state_config

    # Monkeypatch SESSIONS_DIR to use temp directory
    monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)

    from orchestration.state.algorithm_state import AlgorithmState

    def _create(
        user_query: str = "Test query",
        session_id: Optional[str] = None,
        **kwargs,
    ) -> AlgorithmState:
        state = AlgorithmState(
            user_query=user_query,
            session_id=session_id,
            **kwargs,
        )
        return state

    return _create


@pytest.fixture
def saved_algorithm_state(create_algorithm_state):
    """
    Create and save an AlgorithmState.

    Usage:
        state = saved_algorithm_state(user_query="Test")
        # State file now exists on disk
    """

    def _create(**kwargs) -> "AlgorithmState":
        state = create_algorithm_state(**kwargs)
        state.save()
        return state

    return _create


# ==============================================================================
# State Creation Helpers (JSON files)
# ==============================================================================


@pytest.fixture
def create_algorithm_state_file(temp_state_dir: Path):
    """
    Factory fixture to create algorithm state JSON files directly.

    Usage:
        data = create_algorithm_state_file(
            session_id="abc123",
            user_query="Build API",
            fsm_state="GATHER"
        )
    """

    def _create(
        session_id: str,
        user_query: str = "Test query",
        fsm_state: str = "INITIALIZED",
        phase_outputs: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        state_data = {
            "schema_version": "1.0",
            "session_id": session_id,
            "user_query": user_query,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": "initialized" if fsm_state == "INITIALIZED" else "in_progress",
            "fsm": {
                "state": fsm_state,
                "history": [fsm_state],
                "current_step": -1 if fsm_state == "INITIALIZED" else 0,
                "iteration_count": 0,
            },
            "phase_outputs": phase_outputs or {},
            "phase_timestamps": {},
            "ideal_state": {},
            "johari_schema": {},
            "verification_results": [],
            "halt_reason": None,
            "clarification_questions": [],
            "metadata": {},
        }
        state_data.update(kwargs)

        # Write to file
        state_file = temp_state_dir / f"algorithm-{session_id}.json"
        state_file.write_text(json.dumps(state_data, indent=2))

        return state_data

    return _create


# ==============================================================================
# Memory File Helpers
# ==============================================================================


@pytest.fixture
def create_memory_file(temp_memory_dir: Path):
    """
    Factory fixture to create agent memory files.

    Usage:
        path = create_memory_file(task_id, "research", content="...")
    """

    def _create(
        task_id: str,
        agent_name: str,
        content: Optional[str] = None,
        sections: Optional[Dict[str, str]] = None,
    ) -> Path:
        if content is None:
            # Generate valid memory file content
            sections = sections or {
                "Section 0: Context Loaded": f"Task ID: {task_id}\nAgent: {agent_name}",
                "Section 1: Step Overview": "Test step overview content.",
                "Section 2: Johari Summary": "Known Knowns: Test\nKnown Unknowns: Test",
                "Section 3: Downstream Directives": "Test directives for next phase.",
            }

            content = f"# {agent_name.title().replace('-', ' ')} Output: Test Task\n\n"
            for section_name, section_content in sections.items():
                content += f"## {section_name}\n\n{section_content}\n\n"
            content += f"---\n**{agent_name.upper().replace('-', '_')}_COMPLETE**\n"

        memory_file = temp_memory_dir / f"{task_id}-{agent_name}-memory.md"
        memory_file.write_text(content)

        return memory_file

    return _create


@pytest.fixture
def create_valid_memory_file(create_memory_file):
    """
    Create a valid memory file with all required sections.

    Shortcut for create_memory_file with default valid content.
    """

    def _create(task_id: str, agent_name: str) -> Path:
        return create_memory_file(task_id, agent_name)

    return _create


@pytest.fixture
def create_invalid_memory_file(temp_memory_dir: Path):
    """
    Factory to create invalid memory files for testing validation.

    Usage:
        path = create_invalid_memory_file(task_id, "agent", missing_sections=["Section 2"])
    """

    def _create(
        task_id: str,
        agent_name: str,
        missing_sections: Optional[list] = None,
        empty: bool = False,
        too_short: bool = False,
    ) -> Path:
        if empty:
            content = ""
        elif too_short:
            content = "Short content"
        else:
            # Create content with missing sections
            all_sections = {
                "Section 0: Context Loaded": f"Task ID: {task_id}",
                "Section 1: Step Overview": "Step overview.",
                "Section 2: Johari Summary": "Johari content.",
                "Section 3: Downstream Directives": "Directives.",
            }

            missing_sections = missing_sections or []
            for section in missing_sections:
                # Remove sections that match
                keys_to_remove = [k for k in all_sections if section in k]
                for k in keys_to_remove:
                    del all_sections[k]

            content = f"# {agent_name} Output: Test\n\n"
            for section_name, section_content in all_sections.items():
                content += f"## {section_name}\n\n{section_content}\n\n"

        memory_file = temp_memory_dir / f"{task_id}-{agent_name}-memory.md"
        memory_file.write_text(content)

        return memory_file

    return _create


# ==============================================================================
# Cleanup Fixtures
# ==============================================================================


@pytest.fixture
def cleanup_paths():
    """
    Fixture to clean up paths after test.

    Usage:
        def test_something(cleanup_paths):
            # Your test
            cleanup_paths(Path("path/to/clean"))
    """
    paths_to_clean = []

    def _register(path: Path):
        paths_to_clean.append(path)

    yield _register

    for path in paths_to_clean:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


# ==============================================================================
# Monkeypatch Helpers
# ==============================================================================


@pytest.fixture
def mock_sessions_dir(monkeypatch, temp_state_dir: Path):
    """
    Monkeypatch SESSIONS_DIR to use temporary directory.

    Use this when you need to test with isolated state files.
    Patches both config module and algorithm_state module where SESSIONS_DIR is imported.
    """
    from orchestration.state import config as state_config
    from orchestration.state import algorithm_state

    monkeypatch.setattr(state_config, "SESSIONS_DIR", temp_state_dir)
    monkeypatch.setattr(algorithm_state, "SESSIONS_DIR", temp_state_dir)
    return temp_state_dir


# ==============================================================================
# Test Data Fixtures
# ==============================================================================


@pytest.fixture
def sample_user_queries() -> list:
    """Provide sample user queries for testing."""
    return [
        "Help me build a REST API",
        "Research best practices for MCP servers",
        "Create a new skill for code review",
        "Fix the bug in authentication",
        "Simple: what time is it?",
    ]


@pytest.fixture
def sample_agent_names() -> list:
    """Provide sample agent names for testing."""
    return [
        "clarification",
        "research",
        "analysis",
        "synthesis",
        "generation",
        "validation",
        "memory",
    ]


@pytest.fixture
def sample_phases() -> list:
    """Provide sample phase names for testing."""
    from orchestration.state.algorithm_fsm import AlgorithmPhase

    return list(AlgorithmPhase)


# ==============================================================================
# Test Markers Configuration
# ==============================================================================


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    config.addinivalue_line("markers", "fsm: mark test as testing FSM functionality")
    config.addinivalue_line(
        "markers", "critical: mark test as testing critical functionality"
    )
