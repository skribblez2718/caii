"""
Unit tests for agent_chain/state.py
"""

import json
import pytest
from pathlib import Path

from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR


class TestChainState:
    """Tests for ChainState class."""

    def test_creation(self):
        """ChainState should be created with required fields."""
        state = ChainState(
            task_id="test-123",
            flow_id="test-flow",
        )
        assert state.task_id == "test-123"
        assert state.flow_id == "test-flow"
        assert state.current_step_index == 0
        assert state.completed_agents == []
        assert state.memory_files_created == {}

    def test_creation_with_optional_fields(self):
        """ChainState should accept optional fields."""
        state = ChainState(
            task_id="test-123",
            flow_id="test-flow",
            skill_name="tdd",
            phase_id="red",
        )
        assert state.skill_name == "tdd"
        assert state.phase_id == "red"

    def test_mark_agent_complete(self):
        """mark_agent_complete should update state correctly."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        state.mark_agent_complete("clarification", "/path/to/memory.md")

        assert "clarification" in state.completed_agents
        assert state.memory_files_created["clarification"] == "/path/to/memory.md"

    def test_mark_agent_complete_idempotent(self):
        """mark_agent_complete should be idempotent."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        state.mark_agent_complete("clarification", "/path/to/memory.md")
        state.mark_agent_complete("clarification", "/path/to/memory.md")

        assert state.completed_agents.count("clarification") == 1

    def test_advance_step(self):
        """advance_step should increment step index."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        assert state.current_step_index == 0
        state.advance_step()
        assert state.current_step_index == 1
        state.advance_step()
        assert state.current_step_index == 2

    def test_is_agent_completed(self):
        """is_agent_completed should return correct value."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        assert state.is_agent_completed("clarification") is False
        state.mark_agent_complete("clarification", "/path/to/memory.md")
        assert state.is_agent_completed("clarification") is True

    def test_get_memory_file(self):
        """get_memory_file should return correct path."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        assert state.get_memory_file("clarification") is None
        state.mark_agent_complete("clarification", "/path/to/memory.md")
        assert state.get_memory_file("clarification") == "/path/to/memory.md"

    def test_to_dict(self):
        """to_dict should serialize all fields."""
        state = ChainState(
            task_id="test-123",
            flow_id="test-flow",
            skill_name="tdd",
            phase_id="red",
        )
        state.mark_agent_complete("clarification", "/path/to/memory.md")

        data = state.to_dict()

        assert data["task_id"] == "test-123"
        assert data["flow_id"] == "test-flow"
        assert data["skill_name"] == "tdd"
        assert data["phase_id"] == "red"
        assert "clarification" in data["completed_agents"]
        assert data["memory_files_created"]["clarification"] == "/path/to/memory.md"

    def test_from_dict(self):
        """from_dict should deserialize correctly."""
        data = {
            "task_id": "test-123",
            "flow_id": "test-flow",
            "skill_name": "tdd",
            "phase_id": "red",
            "current_step_index": 2,
            "completed_agents": ["clarification", "research"],
            "memory_files_created": {"clarification": "/path/1.md"},
            "started_at": "2024-01-01T00:00:00",
            "metadata": {"key": "value"},
        }

        state = ChainState.from_dict(data)

        assert state.task_id == "test-123"
        assert state.flow_id == "test-flow"
        assert state.skill_name == "tdd"
        assert state.current_step_index == 2
        assert len(state.completed_agents) == 2
        assert state.metadata["key"] == "value"

    def test_save_and_load(self, tmp_path, monkeypatch):
        """save and load should round-trip correctly."""
        # Monkeypatch the state directory
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )

        state = ChainState(
            task_id="test-123",
            flow_id="test-flow",
            skill_name="tdd",
        )
        state.mark_agent_complete("clarification", "/path/to/memory.md")

        # Save
        saved_path = state.save()
        assert saved_path.exists()

        # Load
        loaded = ChainState.load("test-123")
        assert loaded is not None
        assert loaded.task_id == "test-123"
        assert loaded.flow_id == "test-flow"
        assert loaded.is_agent_completed("clarification")

    def test_load_not_found(self, tmp_path, monkeypatch):
        """load should return None if not found."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )

        assert ChainState.load("nonexistent") is None

    def test_load_from_path(self, tmp_path):
        """load_from_path should load from specific path."""
        state = ChainState(task_id="test-123", flow_id="test-flow")
        state_file = tmp_path / "test-state.json"
        state_file.write_text(json.dumps(state.to_dict()))

        loaded = ChainState.load_from_path(state_file)
        assert loaded is not None
        assert loaded.task_id == "test-123"

    def test_load_from_path_not_found(self, tmp_path):
        """load_from_path should return None if file not found."""
        nonexistent = tmp_path / "nonexistent.json"
        assert ChainState.load_from_path(nonexistent) is None


class TestLearningsTracking:
    """Tests for learnings injection tracking."""

    def test_learnings_injected_for_empty_initially(self):
        """learnings_injected_for should be empty on new state."""
        state = ChainState(task_id="test-123", flow_id="test-flow")
        assert state.learnings_injected_for == []

    def test_needs_learnings_directive_first_time(self):
        """needs_learnings_directive should return True for first invocation."""
        state = ChainState(task_id="test-123", flow_id="test-flow")
        assert state.needs_learnings_directive("clarification") is True
        assert state.needs_learnings_directive("research") is True

    def test_needs_learnings_directive_false_after_marked(self):
        """needs_learnings_directive should return False after marking."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        state.mark_learnings_injected("clarification")

        assert state.needs_learnings_directive("clarification") is False
        assert state.needs_learnings_directive("research") is True

    def test_mark_learnings_injected_idempotent(self):
        """mark_learnings_injected should be idempotent."""
        state = ChainState(task_id="test-123", flow_id="test-flow")

        state.mark_learnings_injected("clarification")
        state.mark_learnings_injected("clarification")

        assert state.learnings_injected_for.count("clarification") == 1

    def test_learnings_serialization_to_dict(self):
        """to_dict should include learnings_injected_for."""
        state = ChainState(task_id="test-123", flow_id="test-flow")
        state.mark_learnings_injected("clarification")
        state.mark_learnings_injected("research")

        data = state.to_dict()

        assert "learnings_injected_for" in data
        assert "clarification" in data["learnings_injected_for"]
        assert "research" in data["learnings_injected_for"]

    def test_learnings_deserialization_from_dict(self):
        """from_dict should restore learnings_injected_for."""
        data = {
            "task_id": "test-123",
            "flow_id": "test-flow",
            "learnings_injected_for": ["clarification", "research"],
        }

        state = ChainState.from_dict(data)

        assert state.needs_learnings_directive("clarification") is False
        assert state.needs_learnings_directive("research") is False
        assert state.needs_learnings_directive("analysis") is True

    def test_learnings_deserialization_missing_field(self):
        """from_dict should default to empty list if field missing."""
        data = {
            "task_id": "test-123",
            "flow_id": "test-flow",
            # learnings_injected_for intentionally missing
        }

        state = ChainState.from_dict(data)

        assert state.learnings_injected_for == []
        assert state.needs_learnings_directive("clarification") is True

    def test_learnings_persisted_across_save_load(self, tmp_path, monkeypatch):
        """save and load should persist learnings_injected_for."""
        monkeypatch.setattr(
            "orchestration.agent_chain.state.CHAIN_STATE_DIR",
            tmp_path,
        )

        state = ChainState(task_id="test-123", flow_id="test-flow")
        state.mark_learnings_injected("clarification")
        state.save()

        loaded = ChainState.load("test-123")
        assert loaded is not None
        assert loaded.needs_learnings_directive("clarification") is False
        assert loaded.needs_learnings_directive("research") is True
