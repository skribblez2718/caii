"""
Unit tests for agent completion with flow continuation.

Tests the integration of agents/complete.py with flow_continue.py.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def write_agent_state(state_file: Path, state_data: dict) -> None:
    """Helper to write agent state JSON to a file."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state_data, indent=2))


# ============================================================================
# agent_complete Flow Integration Tests
# ============================================================================


@pytest.mark.unit
class TestAgentCompleteFlowIntegration:
    """Tests for agent_complete() flow continuation integration."""

    def test_agent_complete_calls_flow_continue_when_in_flow(self, tmp_path: Path):
        """agent_complete should call flow_continue.py when in a flow."""
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile
        from datetime import datetime

        task_id = "test-agent-complete-flow"
        agent_name = "clarification"

        # Create chain state
        chain_state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=0,
        )
        chain_state.save()

        # Create agent execution state (write JSON directly for test flexibility)
        state_file = tmp_path / "agent_state.json"
        write_agent_state(
            state_file,
            {
                "agent_name": agent_name,
                "task_id": task_id,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "skill_name": "perform-tdd",
                "phase_id": "red",
                "flow_id": "perform-tdd-red",
                "context_pattern": "WORKFLOW_ONLY",
                "predecessors": [],
                "step_outputs": {},
                "completed_steps": [],
                "metadata": {},
            },
        )

        # Create memory file
        memory_path = MemoryFile.get_path(task_id, agent_name)
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            # Run complete.py with flow-id
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "agents"
                / "complete.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    agent_name,
                    "--state",
                    str(state_file),
                    "--task-id",
                    task_id,
                    "--flow-id",
                    "perform-tdd-red",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed
            assert result.returncode == 0, f"stderr: {result.stderr}"

            # Should print completion marker
            assert "CLARIFICATION_COMPLETE" in result.stdout

            # Should include next agent directive or flow continuation
            # (now calls flow_continue.py which returns directive for research)
            assert (
                "research" in result.stdout.lower()
                or "MANDATORY" in result.stdout
                or "flow" in result.stdout.lower()
            )
        finally:
            # Cleanup
            chain_state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if chain_state_file.exists():
                chain_state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()

    def test_agent_complete_prints_flow_complete_on_last_agent(self, tmp_path: Path):
        """agent_complete should print FLOW_COMPLETE for last agent in flow."""
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.agent_chain.memory import MemoryFile
        from datetime import datetime

        task_id = "test-last-agent-complete"
        agent_name = "generation"

        # Create chain state at last step (DOC has 2 agents)
        chain_state = ChainState(
            task_id=task_id,
            flow_id="perform-tdd-doc",
            skill_name="perform-tdd",
            phase_id="doc",
            current_step_index=1,  # At generation (last step)
            completed_agents=["analysis"],
        )
        chain_state.save()

        # Create agent execution state
        state_file = tmp_path / "agent_state.json"
        write_agent_state(
            state_file,
            {
                "agent_name": agent_name,
                "task_id": task_id,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "skill_name": "perform-tdd",
                "phase_id": "doc",
                "flow_id": "perform-tdd-doc",
                "context_pattern": "IMMEDIATE_PREDECESSORS",
                "predecessors": ["analysis"],
                "step_outputs": {},
                "completed_steps": [],
                "metadata": {},
            },
        )

        # Create memory file
        memory_path = MemoryFile.get_path(task_id, agent_name)
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "agents"
                / "complete.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    agent_name,
                    "--state",
                    str(state_file),
                    "--task-id",
                    task_id,
                    "--flow-id",
                    "perform-tdd-doc",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed
            assert result.returncode == 0, f"stderr: {result.stderr}"

            # Should print completion marker
            assert "GENERATION_COMPLETE" in result.stdout

            # Should print FLOW_COMPLETE marker
            assert "FLOW_COMPLETE" in result.stdout
            assert "perform-tdd-doc" in result.stdout
        finally:
            chain_state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
            if chain_state_file.exists():
                chain_state_file.unlink()
            if memory_path.exists():
                memory_path.unlink()

    def test_agent_complete_no_flow_continues_without_calling_flow_continue(
        self, tmp_path: Path
    ):
        """agent_complete without flow_id should not call flow_continue."""
        from orchestration.agent_chain.memory import MemoryFile
        from datetime import datetime

        task_id = "test-no-flow"
        agent_name = "analysis"

        # Create agent execution state WITHOUT flow_id
        state_file = tmp_path / "agent_state.json"
        write_agent_state(
            state_file,
            {
                "agent_name": agent_name,
                "task_id": task_id,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "skill_name": None,
                "phase_id": None,
                "flow_id": None,  # No flow
                "context_pattern": "WORKFLOW_ONLY",
                "predecessors": [],
                "step_outputs": {},
                "completed_steps": [],
                "metadata": {},
            },
        )

        # Create memory file
        memory_path = MemoryFile.get_path(task_id, agent_name)
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "agents"
                / "complete.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    agent_name,
                    "--state",
                    str(state_file),
                    "--task-id",
                    task_id,
                    # No --flow-id argument
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed
            assert result.returncode == 0, f"stderr: {result.stderr}"

            # Should print completion marker
            assert "ANALYSIS_COMPLETE" in result.stdout

            # Should NOT have flow continuation or MANDATORY directive
            assert "FLOW_COMPLETE" not in result.stdout
        finally:
            if memory_path.exists():
                memory_path.unlink()


# ============================================================================
# Flow Continue Error Handling Tests
# ============================================================================


@pytest.mark.unit
class TestAgentCompleteFlowErrors:
    """Tests for error handling in agent_complete flow integration."""

    def test_agent_complete_handles_flow_continue_error_gracefully(
        self, tmp_path: Path
    ):
        """agent_complete should handle flow_continue.py errors gracefully."""
        from orchestration.agent_chain.memory import MemoryFile
        from datetime import datetime

        task_id = "test-flow-error"
        agent_name = "clarification"

        # Create agent execution state with flow_id but NO chain state
        # (this will cause flow_continue.py to error)
        state_file = tmp_path / "agent_state.json"
        write_agent_state(
            state_file,
            {
                "agent_name": agent_name,
                "task_id": task_id,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "skill_name": "perform-tdd",
                "phase_id": "red",
                "flow_id": "perform-tdd-red",  # Flow ID present
                "context_pattern": "WORKFLOW_ONLY",
                "predecessors": [],
                "step_outputs": {},
                "completed_steps": [],
                "metadata": {},
            },
        )

        # Create memory file
        memory_path = MemoryFile.get_path(task_id, agent_name)
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("# Test memory\n")

        try:
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "agents"
                / "complete.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    agent_name,
                    "--state",
                    str(state_file),
                    "--task-id",
                    task_id,
                    "--flow-id",
                    "perform-tdd-red",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should exit with error (chain state missing)
            assert result.returncode != 0
            # Error message should be in stderr
            assert "ERROR" in result.stderr or "No chain state" in result.stderr
        finally:
            if memory_path.exists():
                memory_path.unlink()
