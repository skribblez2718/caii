"""
Unit tests for decompose/complete.py

Tests the completion handler for DECOMPOSE protocol:
- complete_decomposition(): Create subtask states and route first ready subtask
- on_subtask_complete(): Handle subtask completion and route next
- trigger_aggregation(): Start aggregation flow when all subtasks done
"""

import json
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestCompleteDecomposition:
    """Tests for complete_decomposition function."""

    def test_complete_decomposition_creates_subtask_states(
        self, mock_sessions_dir, monkeypatch
    ):
        """complete_decomposition should create AlgorithmState for each subtask."""
        from orchestration.decompose.complete import complete_decomposition
        from orchestration.state.algorithm_state import AlgorithmState

        # Create parent state
        parent = AlgorithmState(
            user_query="Complex task needing decomposition",
            session_id="parent123456",
            complexity="complex",
        )
        parent.save()

        # Define subtasks from synthesis output
        subtasks = [
            {
                "subtask_id": "ST-001",
                "description": "First subtask",
                "complexity": "simple",
                "dependencies": [],
            },
            {
                "subtask_id": "ST-002",
                "description": "Second subtask",
                "complexity": "simple",
                "dependencies": ["ST-001"],
            },
        ]

        # Execute
        result = complete_decomposition(parent, subtasks)

        # Reload parent to check subtasks registered
        reloaded_parent = AlgorithmState.load("parent123456")
        assert reloaded_parent is not None
        assert len(reloaded_parent.subtasks) == 2

    def test_complete_decomposition_registers_dependencies(
        self, mock_sessions_dir, monkeypatch
    ):
        """complete_decomposition should register subtask dependencies correctly."""
        from orchestration.decompose.complete import complete_decomposition
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Task with dependencies",
            session_id="deps12345678",
            complexity="complex",
        )
        parent.save()

        subtasks = [
            {
                "subtask_id": "ST-001",
                "description": "Independent subtask",
                "complexity": "simple",
                "dependencies": [],
            },
            {
                "subtask_id": "ST-002",
                "description": "Dependent subtask",
                "complexity": "simple",
                "dependencies": ["ST-001"],
            },
        ]

        complete_decomposition(parent, subtasks)

        reloaded = AlgorithmState.load("deps12345678")
        # Should have 2 subtasks registered
        assert len(reloaded.subtasks) == 2
        # Find the subtask that has dependencies (it depends on the other one)
        subtask_with_deps = [
            info for info in reloaded.subtasks.values() if len(info["dependencies"]) > 0
        ]
        assert len(subtask_with_deps) == 1
        assert len(subtask_with_deps[0]["dependencies"]) == 1

    def test_complete_decomposition_returns_gather_directive(
        self, mock_sessions_dir, monkeypatch
    ):
        """complete_decomposition should return directive to route first subtask to GATHER."""
        from orchestration.decompose.complete import complete_decomposition
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Task for gather routing",
            session_id="gather1234567",
            complexity="complex",
        )
        parent.save()

        subtasks = [
            {
                "subtask_id": "ST-001",
                "description": "First subtask to gather",
                "complexity": "simple",
                "dependencies": [],
            },
        ]

        result = complete_decomposition(parent, subtasks)

        # Should return a directive mentioning GATHER
        assert "GATHER" in result or "gather" in result.lower()

    def test_complete_decomposition_saves_state_before_directive(
        self, mock_sessions_dir, monkeypatch
    ):
        """State must be saved before returning directive (critical invariant)."""
        from orchestration.decompose.complete import complete_decomposition
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="State save test",
            session_id="save12345678",
            complexity="complex",
        )
        parent.save()

        subtasks = [
            {
                "subtask_id": "ST-001",
                "description": "Subtask",
                "complexity": "simple",
                "dependencies": [],
            },
        ]

        # Track save calls
        original_save = AlgorithmState.save
        save_called = {"count": 0}

        def mock_save(self):
            save_called["count"] += 1
            return original_save(self)

        monkeypatch.setattr(AlgorithmState, "save", mock_save)

        complete_decomposition(parent, subtasks)

        # Parent state should have been saved
        assert save_called["count"] >= 1


@pytest.mark.unit
class TestOnSubtaskComplete:
    """Tests for on_subtask_complete function."""

    def test_on_subtask_complete_marks_subtask_done(
        self, mock_sessions_dir, monkeypatch
    ):
        """on_subtask_complete should mark the subtask as completed in parent."""
        from orchestration.decompose.complete import on_subtask_complete
        from orchestration.state.algorithm_state import AlgorithmState

        # Create parent with subtasks
        parent = AlgorithmState(
            user_query="Parent task",
            session_id="parent654321",
            complexity="complex",
        )
        parent.subtasks = {
            "subtask00001": {"dependencies": [], "complete": False},
            "subtask00002": {"dependencies": ["subtask00001"], "complete": False},
        }
        parent.save()

        # Create subtask state
        subtask = AlgorithmState(
            user_query="First subtask",
            session_id="subtask00001",
            complexity="simple",
            parent_task_id="parent654321",
            subtask_index=0,
        )
        subtask.save()

        # Complete subtask
        result = on_subtask_complete(subtask)

        # Reload parent and check
        reloaded_parent = AlgorithmState.load("parent654321")
        assert reloaded_parent.subtasks["subtask00001"]["complete"] is True

    def test_on_subtask_complete_returns_next_subtask_directive(
        self, mock_sessions_dir, monkeypatch
    ):
        """on_subtask_complete should return directive for next ready subtask."""
        from orchestration.decompose.complete import on_subtask_complete
        from orchestration.state.algorithm_state import AlgorithmState

        # Create parent with subtasks where second depends on first
        parent = AlgorithmState(
            user_query="Parent task",
            session_id="parent111222",
            complexity="complex",
        )
        parent.subtasks = {
            "sub001aaaaaa": {"dependencies": [], "complete": False},
            "sub002bbbbbb": {"dependencies": ["sub001aaaaaa"], "complete": False},
        }
        parent.save()

        # Create and complete first subtask
        subtask1 = AlgorithmState(
            user_query="First subtask",
            session_id="sub001aaaaaa",
            complexity="simple",
            parent_task_id="parent111222",
            subtask_index=0,
        )
        subtask1.save()

        result = on_subtask_complete(subtask1)

        # Should return directive for next subtask (GATHER)
        assert result is not None
        assert "GATHER" in result or "gather" in result.lower() or "sub002" in result

    def test_on_subtask_complete_triggers_aggregation_when_all_done(
        self, mock_sessions_dir, monkeypatch
    ):
        """on_subtask_complete should trigger aggregation when all subtasks complete."""
        from orchestration.decompose.complete import on_subtask_complete
        from orchestration.state.algorithm_state import AlgorithmState

        # Create parent with single subtask
        parent = AlgorithmState(
            user_query="Parent task",
            session_id="parent333444",
            complexity="complex",
        )
        parent.subtasks = {
            "onlysub12345": {"dependencies": [], "complete": False},
        }
        parent.save()

        # Create subtask
        subtask = AlgorithmState(
            user_query="Only subtask",
            session_id="onlysub12345",
            complexity="simple",
            parent_task_id="parent333444",
            subtask_index=0,
        )
        subtask.save()

        result = on_subtask_complete(subtask)

        # Should trigger aggregation
        assert result is not None
        assert "aggregat" in result.lower() or "AGGREGATION" in result

    def test_on_subtask_complete_returns_none_for_non_subtask(
        self, mock_sessions_dir, monkeypatch
    ):
        """on_subtask_complete should return None if state is not a subtask."""
        from orchestration.decompose.complete import on_subtask_complete
        from orchestration.state.algorithm_state import AlgorithmState

        # Create non-subtask state (no parent_task_id)
        state = AlgorithmState(
            user_query="Regular task",
            session_id="regular12345",
            complexity="simple",
        )
        state.save()

        result = on_subtask_complete(state)

        assert result is None


@pytest.mark.unit
class TestTriggerAggregation:
    """Tests for trigger_aggregation function."""

    def test_trigger_aggregation_returns_flow_directive(
        self, mock_sessions_dir, monkeypatch
    ):
        """trigger_aggregation should return directive for AGGREGATION_FLOW."""
        from orchestration.decompose.complete import trigger_aggregation
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Parent for aggregation",
            session_id="aggr12345678",
            complexity="complex",
        )
        parent.subtasks = {
            "sub1_1234567": {"dependencies": [], "complete": True},
            "sub2_1234567": {"dependencies": [], "complete": True},
        }
        parent.save()

        result = trigger_aggregation(parent)

        # Should return directive with aggregation flow
        assert result is not None
        assert "synthesis" in result.lower() or "aggregat" in result.lower()

    def test_trigger_aggregation_uses_parent_session_id(
        self, mock_sessions_dir, monkeypatch
    ):
        """trigger_aggregation should use parent's session_id as task_id."""
        from orchestration.decompose.complete import trigger_aggregation
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Parent session test",
            session_id="parentsess12",
            complexity="complex",
        )
        parent.subtasks = {
            "sub_done_123": {"dependencies": [], "complete": True},
        }
        parent.save()

        result = trigger_aggregation(parent)

        # Directive should reference parent session
        assert "parentsess12" in result


@pytest.mark.unit
class TestSubtaskDependencyOrdering:
    """Tests for correct subtask ordering based on dependencies."""

    def test_independent_subtasks_can_run_in_any_order(
        self, mock_sessions_dir, monkeypatch
    ):
        """Subtasks with no dependencies should all be ready."""
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Parallel subtasks",
            session_id="parallel1234",
            complexity="complex",
        )
        parent.subtasks = {
            "ind1_1234567": {"dependencies": [], "complete": False},
            "ind2_1234567": {"dependencies": [], "complete": False},
            "ind3_1234567": {"dependencies": [], "complete": False},
        }
        parent.save()

        ready = parent.get_ready_subtasks()

        # All three should be ready
        assert len(ready) == 3

    def test_dependent_subtask_blocked_until_dependency_complete(
        self, mock_sessions_dir, monkeypatch
    ):
        """Subtask with dependency should not be ready until dependency completes."""
        from orchestration.state.algorithm_state import AlgorithmState

        parent = AlgorithmState(
            user_query="Sequential subtasks",
            session_id="seq123456789",
            complexity="complex",
        )
        parent.subtasks = {
            "first_123456": {"dependencies": [], "complete": False},
            "second_12345": {"dependencies": ["first_123456"], "complete": False},
        }
        parent.save()

        ready_before = parent.get_ready_subtasks()
        assert "first_123456" in ready_before
        assert "second_12345" not in ready_before

        # Complete first subtask
        parent.mark_subtask_complete("first_123456")

        ready_after = parent.get_ready_subtasks()
        assert "second_12345" in ready_after
