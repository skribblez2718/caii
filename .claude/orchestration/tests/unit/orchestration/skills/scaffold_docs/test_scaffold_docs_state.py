"""
Scaffold-Docs State Unit Tests

Tests for ScaffoldDocsPhase, ScaffoldDocsFSM, and ScaffoldDocsState classes.
"""

import json
from pathlib import Path

import pytest


# ==============================================================================
# ScaffoldDocsPhase Enum Tests
# ==============================================================================


@pytest.mark.unit
class TestScaffoldDocsPhase:
    """Tests for ScaffoldDocsPhase enum."""

    def test_phase_values_exist(self):
        """ScaffoldDocsPhase should have all required phases."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsPhase,
        )

        assert hasattr(ScaffoldDocsPhase, "INITIALIZED")
        assert hasattr(ScaffoldDocsPhase, "CLARIFICATION")
        assert hasattr(ScaffoldDocsPhase, "ANALYSIS")
        assert hasattr(ScaffoldDocsPhase, "SYNTHESIS")
        assert hasattr(ScaffoldDocsPhase, "VALIDATION")
        assert hasattr(ScaffoldDocsPhase, "COMPLETED")

    def test_phase_ordering(self):
        """Phases should be in expected order."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsPhase,
        )

        phases = list(ScaffoldDocsPhase)
        phase_names = [p.name for p in phases]

        assert phase_names.index("INITIALIZED") < phase_names.index("CLARIFICATION")
        assert phase_names.index("CLARIFICATION") < phase_names.index("ANALYSIS")
        assert phase_names.index("ANALYSIS") < phase_names.index("SYNTHESIS")
        assert phase_names.index("SYNTHESIS") < phase_names.index("VALIDATION")
        assert phase_names.index("VALIDATION") < phase_names.index("COMPLETED")


# ==============================================================================
# ScaffoldDocsFSM Tests
# ==============================================================================


@pytest.mark.unit
@pytest.mark.fsm
class TestScaffoldDocsFSM:
    """Tests for scaffold-docs finite state machine."""

    def test_initial_state_is_initialized(self):
        """FSM should start in INITIALIZED state."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM()

        assert fsm.state == ScaffoldDocsPhase.INITIALIZED

    def test_default_mode_is_scaffold(self):
        """FSM should default to scaffold mode."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
        )

        fsm = ScaffoldDocsFSM()

        assert fsm.mode == "scaffold"

    def test_scaffold_mode_transitions(self):
        """FSM should follow scaffold mode transitions."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM(mode="scaffold")

        assert fsm.transition(ScaffoldDocsPhase.CLARIFICATION)
        assert fsm.transition(ScaffoldDocsPhase.ANALYSIS)
        assert fsm.transition(ScaffoldDocsPhase.SYNTHESIS)
        assert fsm.transition(ScaffoldDocsPhase.VALIDATION)
        assert fsm.transition(ScaffoldDocsPhase.COMPLETED)
        assert fsm.state == ScaffoldDocsPhase.COMPLETED

    def test_update_mode_skips_clarification(self):
        """Update mode should skip CLARIFICATION phase."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM(mode="update")

        # Should go directly from INITIALIZED to ANALYSIS
        assert fsm.transition(ScaffoldDocsPhase.ANALYSIS)
        assert fsm.state == ScaffoldDocsPhase.ANALYSIS

    def test_update_mode_rejects_clarification(self):
        """Update mode should reject CLARIFICATION transition."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM(mode="update")

        # Should not allow CLARIFICATION in update mode
        assert not fsm.transition(ScaffoldDocsPhase.CLARIFICATION)
        assert fsm.state == ScaffoldDocsPhase.INITIALIZED

    def test_scaffold_mode_rejects_skipping_clarification(self):
        """Scaffold mode should reject skipping CLARIFICATION."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM(mode="scaffold")

        # Should not allow skipping to ANALYSIS
        assert not fsm.transition(ScaffoldDocsPhase.ANALYSIS)
        assert fsm.state == ScaffoldDocsPhase.INITIALIZED

    def test_fsm_serialization(self):
        """FSM should serialize and deserialize correctly."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsFSM,
            ScaffoldDocsPhase,
        )

        fsm = ScaffoldDocsFSM(mode="update")
        fsm.transition(ScaffoldDocsPhase.ANALYSIS)

        data = fsm.to_dict()
        restored = ScaffoldDocsFSM.from_dict(data)

        assert restored.state == ScaffoldDocsPhase.ANALYSIS
        assert restored.mode == "update"


# ==============================================================================
# ScaffoldDocsState Tests
# ==============================================================================


@pytest.mark.unit
class TestScaffoldDocsState:
    """Tests for ScaffoldDocsState."""

    def test_state_creation(self):
        """State should be created with default values."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
            ScaffoldDocsPhase,
        )

        state = ScaffoldDocsState(
            parent_algorithm_id="parent123",
            target_path="/home/user/project",
            mode="scaffold",
        )

        assert state.parent_algorithm_id == "parent123"
        assert state.target_path == "/home/user/project"
        assert state.mode == "scaffold"
        assert state.current_phase == ScaffoldDocsPhase.INITIALIZED
        assert state.created_files == []
        assert state.updated_files == []

    def test_for_algorithm_factory(self):
        """for_algorithm factory should create linked state."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
        )

        state = ScaffoldDocsState.for_algorithm(
            "alg123",
            target_path="/path/to/project",
            mode="update",
        )

        assert state.parent_algorithm_id == "alg123"
        assert state.target_path == "/path/to/project"
        assert state.mode == "update"

    def test_phase_advancement_scaffold_mode(self):
        """State should advance through scaffold mode phases."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
            ScaffoldDocsPhase,
        )

        state = ScaffoldDocsState(mode="scaffold")

        assert state.advance_to_phase(ScaffoldDocsPhase.CLARIFICATION)
        assert state.current_phase == ScaffoldDocsPhase.CLARIFICATION

        assert state.advance_to_phase(ScaffoldDocsPhase.ANALYSIS)
        assert state.current_phase == ScaffoldDocsPhase.ANALYSIS

    def test_phase_advancement_update_mode(self):
        """State should advance through update mode phases."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
            ScaffoldDocsPhase,
        )

        state = ScaffoldDocsState(mode="update")

        assert state.advance_to_phase(ScaffoldDocsPhase.ANALYSIS)
        assert state.current_phase == ScaffoldDocsPhase.ANALYSIS

    def test_file_tracking(self):
        """State should track created and updated files."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
        )

        state = ScaffoldDocsState()

        state.add_created_file("CLAUDE.md")
        state.add_created_file(".claude/rules/general.md")
        state.add_updated_file("docs/README.md")

        assert "CLAUDE.md" in state.created_files
        assert ".claude/rules/general.md" in state.created_files
        assert "docs/README.md" in state.updated_files
        assert len(state.created_files) == 2
        assert len(state.updated_files) == 1

    def test_file_tracking_deduplication(self):
        """State should not add duplicate files."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
        )

        state = ScaffoldDocsState()

        state.add_created_file("CLAUDE.md")
        state.add_created_file("CLAUDE.md")

        assert len(state.created_files) == 1

    def test_phase_output_recording(self):
        """State should record phase outputs."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
            ScaffoldDocsPhase,
        )

        state = ScaffoldDocsState()
        state.advance_to_phase(ScaffoldDocsPhase.CLARIFICATION)

        state.record_phase_output(
            ScaffoldDocsPhase.CLARIFICATION,
            {"project_name": "My Project", "commands": ["npm test"]},
        )

        assert "CLARIFICATION" in state.phase_outputs
        assert state.phase_outputs["CLARIFICATION"]["project_name"] == "My Project"

    def test_state_serialization(self):
        """State should serialize and deserialize correctly."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
            ScaffoldDocsPhase,
        )

        state = ScaffoldDocsState(
            parent_algorithm_id="parent123",
            target_path="/home/user/project",
            mode="scaffold",
            detected_language="python",
        )
        state.advance_to_phase(ScaffoldDocsPhase.CLARIFICATION)
        state.add_created_file("CLAUDE.md")

        data = state.to_dict()
        restored = ScaffoldDocsState.from_dict(data)

        assert restored.parent_algorithm_id == "parent123"
        assert restored.target_path == "/home/user/project"
        assert restored.mode == "scaffold"
        assert restored.detected_language == "python"
        assert restored.current_phase == ScaffoldDocsPhase.CLARIFICATION
        assert "CLAUDE.md" in restored.created_files

    def test_persistence_config(self):
        """State should return correct persistence config."""
        from orchestration.skills.scaffold_docs.scaffold_docs_state import (
            ScaffoldDocsState,
        )

        sessions_dir, prefix, version = ScaffoldDocsState.get_persistence_config()

        assert "scaffold_docs" in str(sessions_dir)
        assert prefix == "scaffold-docs"
        assert version == "1.0"
