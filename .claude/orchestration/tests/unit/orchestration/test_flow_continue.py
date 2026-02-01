"""
Unit tests for flow_continue.py

Tests the flow continuation script that continues agent chains.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ============================================================================
# flow_continue CLI Tests
# ============================================================================


@pytest.mark.unit
class TestFlowContinueCLI:
    """Tests for flow_continue.py CLI script."""

    def test_flow_continue_prints_next_directive(self, tmp_path: Path):
        """flow_continue.py should print next agent directive when flow continues."""
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile

        # Create chain state
        task_id = "test-continue-123"
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=0,
            completed_agents=[],
        )
        state.save()

        # Create memory file for clarification agent
        memory_path = MemoryFile.get_path(task_id, "clarification")
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            # Run flow_continue.py
            script_path = (
                Path(__file__).parent.parent.parent.parent / "flow_continue.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--task-id",
                    task_id,
                    "--completed-agent",
                    "clarification",
                ],
                capture_output=True,
                text=True,
            )

            # Should succeed and print next directive
            assert result.returncode == 0
            # Should contain directive for next agent (research)
            assert "research" in result.stdout.lower() or "MANDATORY" in result.stdout
        finally:
            # Cleanup
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()

    def test_flow_continue_prints_flow_complete_when_done(self, tmp_path: Path):
        """flow_continue.py should print FLOW_COMPLETE when all agents done."""
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile
        from orchestration.skills.perform_tdd.flows import TDD_DOC_FLOW

        # Create chain state at the last step (DOC has 2 agents: analysis, generation)
        task_id = "test-complete-456"
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-doc",
            skill_name="perform-tdd",
            phase_id="doc",
            current_step_index=1,  # At generation (second/last step)
            completed_agents=["analysis"],
        )
        state.save()

        # Create memory file for generation agent
        memory_path = MemoryFile.get_path(task_id, "generation")
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            # Run flow_continue.py
            script_path = (
                Path(__file__).parent.parent.parent.parent / "flow_continue.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--task-id",
                    task_id,
                    "--completed-agent",
                    "generation",
                ],
                capture_output=True,
                text=True,
            )

            # Should succeed and print FLOW_COMPLETE
            assert result.returncode == 0
            assert "FLOW_COMPLETE" in result.stdout
            assert "perform-tdd-doc" in result.stdout
        finally:
            # Cleanup
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()

    def test_flow_continue_errors_on_missing_state(self):
        """flow_continue.py should error when chain state not found."""
        script_path = Path(__file__).parent.parent.parent.parent / "flow_continue.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--task-id",
                "nonexistent-task-id",
                "--completed-agent",
                "clarification",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "ERROR" in result.stderr or "No chain state" in result.stderr

    def test_flow_continue_errors_on_unknown_flow(self, tmp_path: Path):
        """flow_continue.py should error when flow ID not in registry."""
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        task_id = "test-unknown-flow-789"
        state = ChainState(
            task_id=task_id,
            flow_id="unknown-flow-that-does-not-exist",
            skill_name="unknown",
            phase_id="test",
        )
        state.save()

        try:
            script_path = (
                Path(__file__).parent.parent.parent.parent / "flow_continue.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--task-id",
                    task_id,
                    "--completed-agent",
                    "clarification",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0
            assert "ERROR" in result.stderr or "Unknown flow" in result.stderr
        finally:
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()


# ============================================================================
# flow_continue Function Tests
# ============================================================================


@pytest.mark.unit
class TestFlowContinueLogic:
    """Tests for flow_continue internal logic."""

    def test_continue_flow_uses_chain_orchestrator(self):
        """Flow continuation should use ChainOrchestrator.get_next_directive."""
        from orchestration.agent_chain.state import ChainState
        from orchestration.agent_chain.orchestrator import ChainOrchestrator
        from orchestration.skills.perform_tdd.flows import TDD_RED_FLOW
        from orchestration.flow_registry import get_flow

        # Verify TDD RED flow is registered
        flow = get_flow("perform-tdd-red")
        assert flow is not None
        assert flow == TDD_RED_FLOW

        # Verify ChainOrchestrator has get_next_directive method
        assert hasattr(ChainOrchestrator, "get_next_directive")

    def test_chain_orchestrator_get_next_directive(self):
        """ChainOrchestrator.get_next_directive should return directive or None."""
        from orchestration.agent_chain.orchestrator import ChainOrchestrator
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile
        from orchestration.skills.perform_tdd.flows import TDD_DOC_FLOW

        task_id = "test-orchestrator-next"

        # Create memory for analysis agent
        memory_path = MemoryFile.get_path(task_id, "analysis")
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Analysis output\n")

        try:
            orchestrator = ChainOrchestrator(
                flow=TDD_DOC_FLOW,
                task_id=task_id,
                skill_name="perform-tdd",
                phase_id="doc",
            )

            # Get next directive after analysis completes
            directive = orchestrator.get_next_directive("analysis")

            # Should return directive for generation (next agent)
            assert directive is not None
            assert "generation" in directive.lower() or "MANDATORY" in directive
        finally:
            # Cleanup
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()

    def test_chain_orchestrator_returns_none_when_complete(self):
        """ChainOrchestrator.get_next_directive should return None when flow complete."""
        from orchestration.agent_chain.orchestrator import ChainOrchestrator
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile
        from orchestration.skills.perform_tdd.flows import TDD_DOC_FLOW

        task_id = "test-orchestrator-complete"

        # Create state already at last step
        state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-doc",
            skill_name="perform-tdd",
            phase_id="doc",
            current_step_index=1,  # At generation (last step)
            completed_agents=["analysis"],
        )
        state.save()

        # Create memory for generation agent
        memory_path = MemoryFile.get_path(task_id, "generation")
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Generation output\n")

        try:
            orchestrator = ChainOrchestrator(
                flow=TDD_DOC_FLOW,
                task_id=task_id,
                skill_name="perform-tdd",
                phase_id="doc",
            )

            # Get next directive after generation completes
            directive = orchestrator.get_next_directive("generation")

            # Should return None (flow complete)
            assert directive is None
        finally:
            # Cleanup
            state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if state_file.exists():
                state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()
