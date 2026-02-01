"""
Unit tests for TDD advance.py flow completion gate.

Tests that phase advancement is blocked until the current phase's
agent flow has completed all agents.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# ============================================================================
# Flow Completion Gate Tests
# ============================================================================


@pytest.mark.unit
class TestAdvanceFlowGate:
    """Tests for flow completion gate in advance.py."""

    def test_advance_blocks_when_flow_not_complete(self):
        """advance.py should block when current phase flow is incomplete."""
        from orchestration.skills.perform_tdd.tdd_state import (
            TDDPhase,
            TDDState,
            TDD_SESSIONS_DIR,
        )
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        # Create TDD state in RED phase
        tdd_state = TDDState()
        tdd_state.advance_to_phase(TDDPhase.RED)
        tdd_state.save()

        # Create chain state showing only first agent done (not all 4)
        chain_state = ChainState(
            task_id=tdd_state.session_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=1,  # Only clarification done (RED has 4 agents)
            completed_agents=["clarification"],
        )
        chain_state.save()

        try:
            # Run advance.py
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "skills"
                / "perform_tdd"
                / "advance.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--perform-tdd-state",
                    tdd_state.session_id,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should fail with flow not complete error
            assert result.returncode != 0
            assert (
                "flow" in result.stderr.lower()
                or "not complete" in result.stderr.lower()
            )
        finally:
            # Cleanup TDD state
            tdd_file = TDD_SESSIONS_DIR / f"perform-tdd-{tdd_state.session_id}.json"
            if tdd_file.exists():
                tdd_file.unlink()
            # Cleanup chain state
            chain_file = CHAIN_STATE_DIR / f"chain-{tdd_state.session_id}.json"
            if chain_file.exists():
                chain_file.unlink()

    def test_advance_succeeds_when_flow_complete(self):
        """advance.py should succeed when current phase flow is complete."""
        from orchestration.skills.perform_tdd.tdd_state import (
            TDDPhase,
            TDDState,
            TDD_SESSIONS_DIR,
        )
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        # Create TDD state in RED phase
        tdd_state = TDDState()
        tdd_state.advance_to_phase(TDDPhase.RED)
        tdd_state.save()

        # Create chain state showing ALL agents done (RED has 4 agents)
        chain_state = ChainState(
            task_id=tdd_state.session_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=4,  # All 4 agents done
            completed_agents=["clarification", "research", "analysis", "generation"],
        )
        chain_state.save()

        try:
            # Run advance.py
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "skills"
                / "perform_tdd"
                / "advance.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--perform-tdd-state",
                    tdd_state.session_id,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed and advance to GREEN
            assert result.returncode == 0, f"stderr: {result.stderr}"
            assert "GREEN" in result.stdout
        finally:
            # Cleanup TDD state
            tdd_file = TDD_SESSIONS_DIR / f"perform-tdd-{tdd_state.session_id}.json"
            if tdd_file.exists():
                tdd_file.unlink()
            # Cleanup chain state
            chain_file = CHAIN_STATE_DIR / f"chain-{tdd_state.session_id}.json"
            if chain_file.exists():
                chain_file.unlink()

    def test_advance_skips_gate_with_no_flow_flag(self):
        """advance.py --no-flow should skip the flow completion gate."""
        from orchestration.skills.perform_tdd.tdd_state import (
            TDDPhase,
            TDDState,
            TDD_SESSIONS_DIR,
        )
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR

        # Create TDD state in RED phase
        tdd_state = TDDState()
        tdd_state.advance_to_phase(TDDPhase.RED)
        tdd_state.save()

        # Create chain state showing incomplete flow
        chain_state = ChainState(
            task_id=tdd_state.session_id,
            flow_id="perform-tdd-red",
            skill_name="perform-tdd",
            phase_id="red",
            current_step_index=1,  # Incomplete
            completed_agents=["clarification"],
        )
        chain_state.save()

        try:
            # Run advance.py with --no-flow
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "skills"
                / "perform_tdd"
                / "advance.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--perform-tdd-state",
                    tdd_state.session_id,
                    "--no-flow",  # Skip gate
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed because --no-flow skips the gate
            assert result.returncode == 0, f"stderr: {result.stderr}"
            assert "GREEN" in result.stdout
        finally:
            # Cleanup
            tdd_file = TDD_SESSIONS_DIR / f"perform-tdd-{tdd_state.session_id}.json"
            if tdd_file.exists():
                tdd_file.unlink()
            chain_file = CHAIN_STATE_DIR / f"chain-{tdd_state.session_id}.json"
            if chain_file.exists():
                chain_file.unlink()

    def test_advance_works_without_chain_state_in_no_flow_mode(self):
        """advance.py --no-flow should work even without chain state."""
        from orchestration.skills.perform_tdd.tdd_state import (
            TDDPhase,
            TDDState,
            TDD_SESSIONS_DIR,
        )

        # Create TDD state in RED phase
        tdd_state = TDDState()
        tdd_state.advance_to_phase(TDDPhase.RED)
        tdd_state.save()

        # NO chain state created

        try:
            # Run advance.py with --no-flow
            script_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "skills"
                / "perform_tdd"
                / "advance.py"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--perform-tdd-state",
                    tdd_state.session_id,
                    "--no-flow",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed (--no-flow skips gate check entirely)
            assert result.returncode == 0, f"stderr: {result.stderr}"
        finally:
            # Cleanup
            tdd_file = TDD_SESSIONS_DIR / f"perform-tdd-{tdd_state.session_id}.json"
            if tdd_file.exists():
                tdd_file.unlink()


# ============================================================================
# is_flow_complete Integration Tests
# ============================================================================


@pytest.mark.unit
class TestIsFlowCompleteIntegration:
    """Integration tests for is_flow_complete with TDD phases."""

    def test_is_flow_complete_for_all_tdd_phases(self):
        """is_flow_complete should work for all TDD phase flows."""
        from orchestration.flow_invoker import is_flow_complete
        from orchestration.agent_chain.state import ChainState, CHAIN_STATE_DIR
        from orchestration.skills.perform_tdd.flows import TDD_PHASE_FLOWS

        for phase_name, flow in TDD_PHASE_FLOWS.items():
            task_id = f"test-{phase_name.lower()}-complete"

            # Create state showing all agents done
            state = ChainState(
                task_id=task_id,
                flow_id=flow.flow_id,
                skill_name="perform-tdd",
                phase_id=phase_name.lower(),
                current_step_index=len(flow.steps),  # All done
                completed_agents=[s.agent_name for s in flow.steps],
            )
            state.save()

            try:
                result = is_flow_complete(task_id, flow.flow_id)
                assert result is True, f"Flow {flow.flow_id} should be complete"
            finally:
                state_file = CHAIN_STATE_DIR / f"chain-{task_id}.json"
                if state_file.exists():
                    state_file.unlink()
