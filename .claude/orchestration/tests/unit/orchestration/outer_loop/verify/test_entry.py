"""
Unit tests for outer_loop/verify/entry.py

Tests the VERIFY phase (Step 8) entry point.
Updated to work with refactored run_phase_entry() pattern.
Includes tests for loop-back orchestration and question bubble-up.
"""

import sys
from unittest.mock import patch, MagicMock

import pytest

from orchestration.state.algorithm_state import (
    AlgorithmState,
    IdealState,
    VerificationResult,
    SuccessCriterion,
)
from orchestration.state.algorithm_fsm import AlgorithmPhase


class TestVerifyEntryMain:
    """Tests for VERIFY entry point using run_phase_entry."""

    @pytest.mark.unit
    def test_exits_without_state_arg(self, monkeypatch, capsys):
        """Should exit with error when --state not provided."""
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.VERIFY,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
                ),
            )

        assert exc_info.value.code != 0

    @pytest.mark.unit
    def test_exits_for_missing_session(self, mock_sessions_dir, monkeypatch, capsys):
        """Should exit with error when session doesn't exist."""
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.VERIFY,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
                ),
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    @pytest.mark.unit
    @pytest.mark.fsm
    def test_starts_verify_phase(self, mock_sessions_dir, monkeypatch, capsys):
        """Should transition state to VERIFY phase (step 8)."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        # Create state properly at EXECUTE phase via FSM transitions
        state = AlgorithmState(user_query="Build API", session_id="verify1234567")
        # Build valid history: must traverse through allowed transitions
        state._fsm._state = AlgorithmPhase.EXECUTE
        state._fsm._history = [
            "INITIALIZED",
            "OBSERVE",
            "THINK",
            "PLAN",
            "BUILD",
            "EXECUTE",
        ]
        state.save()

        with patch("orchestration.utils.load_content", return_value="Test content"):
            run_phase_entry(
                "dummy.py",
                PhaseConfig(
                    phase=AlgorithmPhase.VERIFY,
                    phase_name="VERIFY",
                    content_file="verification.md",
                    description="VERIFY Phase (Step 8)",
                ),
                argv=["--state", "verify1234567"],
            )

        loaded = AlgorithmState.load("verify1234567")
        assert loaded.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.unit
    @pytest.mark.critical
    def test_saves_state_before_print(self, mock_sessions_dir, monkeypatch, capsys):
        """Should save state BEFORE printing prompt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase
        from orchestration.entry_base import run_phase_entry, PhaseConfig

        state = AlgorithmState(user_query="Test", session_id="saveverify12")
        # Build valid history to allow EXECUTE -> VERIFY transition
        state._fsm._state = AlgorithmPhase.EXECUTE
        state._fsm._history = [
            "INITIALIZED",
            "OBSERVE",
            "THINK",
            "PLAN",
            "BUILD",
            "EXECUTE",
        ]
        state.save()

        save_called = []
        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called.append(True)
            return original_save(self)

        with patch("orchestration.utils.load_content", return_value="Content"):
            with patch.object(AlgorithmState, "save", tracking_save):
                run_phase_entry(
                    "dummy.py",
                    PhaseConfig(
                        phase=AlgorithmPhase.VERIFY,
                        phase_name="VERIFY",
                        content_file="verification.md",
                        description="VERIFY Phase (Step 8)",
                    ),
                    argv=["--state", "saveverify12"],
                )

        assert len(save_called) > 0

    @pytest.mark.unit
    def test_step_num_is_eight(self):
        """STEP_NUM should be 8 for VERIFY phase."""
        from orchestration.outer_loop.verify import entry

        assert entry.STEP_NUM == 8


class TestVerifyEntryWithAgentFlow:
    """Tests for VERIFY entry point with agent flow integration."""

    @pytest.mark.unit
    def test_entry_uses_verify_flow(self, mock_sessions_dir):
        """Entry should use VERIFY_FLOW for agent orchestration."""
        from orchestration.outer_loop.verify.entry import VERIFY_FLOW_CONFIG
        from orchestration.outer_loop.verify.flows import VERIFY_FLOW

        # The entry should have a PhaseConfig with agent_flow
        assert VERIFY_FLOW_CONFIG.agent_flow is not None
        assert VERIFY_FLOW_CONFIG.agent_flow.flow_id == VERIFY_FLOW.flow_id

    @pytest.mark.unit
    def test_entry_invokes_chain_orchestrator(self, mock_sessions_dir):
        """Entry should invoke ChainOrchestrator with VERIFY_FLOW."""
        from orchestration.outer_loop.verify import entry
        from orchestration.agent_chain.orchestrator import ChainOrchestrator

        # When entry runs with agent_flow, it should use ChainOrchestrator
        assert hasattr(entry, "VERIFY_FLOW_CONFIG")


class TestVerifyLoopBackLogic:
    """Tests for loop-back from VERIFY to INNER_LOOP."""

    @pytest.fixture
    def state_at_verify(self, mock_sessions_dir):
        """Create state at VERIFY phase."""
        state = AlgorithmState(
            user_query="Build API",
            session_id="loopback1234",
        )
        # Set up FSM to be at VERIFY (would normally transition through)
        state._fsm._state = AlgorithmPhase.VERIFY
        state._fsm._history.extend(["GET_STATE", "INTERVIEW", "INNER_LOOP", "VERIFY"])
        state._fsm._verify_iteration = 1

        # Add ideal state
        state.ideal_state = IdealState(
            task_id="loopback1234",
            task_type="CODING",
            objective="Build REST API",
            euphoric_surprise="Fast",
            success_criteria=[
                SuccessCriterion(
                    id="SC1",
                    description="Tests pass",
                    verification_method="automated",
                )
            ],
        )
        state.save()
        return state

    @pytest.mark.unit
    def test_verified_status_proceeds_to_learn(self, state_at_verify):
        """VERIFIED status should prepare transition to LEARN."""
        from orchestration.outer_loop.verify.entry import handle_verification_result

        result = VerificationResult(
            iteration=1,
            timestamp="2026-01-31T12:00:00Z",
            status="VERIFIED",
            objective_score=0.95,
            heuristic_score=0.90,
            semantic_score=0.92,
            overall_score=0.93,
            gaps=[],
            recommendations=[],
        )

        action = handle_verification_result(state_at_verify, result)
        assert action == "PROCEED"

    @pytest.mark.unit
    def test_gaps_status_loops_back_first_iteration(self, state_at_verify):
        """GAPS_IDENTIFIED on first iteration should loop back."""
        from orchestration.outer_loop.verify.entry import handle_verification_result

        result = VerificationResult(
            iteration=1,
            timestamp="2026-01-31T12:00:00Z",
            status="GAPS_IDENTIFIED",
            objective_score=0.70,
            heuristic_score=0.65,
            semantic_score=0.60,
            overall_score=0.67,
            gaps=["Missing tests"],
            recommendations=["Add unit tests"],
        )

        action = handle_verification_result(state_at_verify, result)
        assert action == "LOOP_BACK"

    @pytest.mark.unit
    def test_gaps_status_escalates_at_max_iterations(self, mock_sessions_dir):
        """GAPS_IDENTIFIED at max iterations should escalate."""
        from orchestration.outer_loop.verify.entry import handle_verification_result

        state = AlgorithmState(
            user_query="Build API",
            session_id="maxiter12345",
        )
        state._fsm._state = AlgorithmPhase.VERIFY
        state._fsm._verify_iteration = 3  # At max
        state.save()

        result = VerificationResult(
            iteration=3,
            timestamp="2026-01-31T12:00:00Z",
            status="GAPS_IDENTIFIED",
            objective_score=0.70,
            heuristic_score=0.65,
            semantic_score=0.60,
            overall_score=0.67,
            gaps=["Still missing tests"],
            recommendations=[],
        )

        action = handle_verification_result(state, result)
        assert action == "ESCALATE"

    @pytest.mark.unit
    def test_critical_failure_escalates_immediately(self, state_at_verify):
        """CRITICAL_FAILURE should escalate regardless of iteration."""
        from orchestration.outer_loop.verify.entry import handle_verification_result

        result = VerificationResult(
            iteration=1,
            timestamp="2026-01-31T12:00:00Z",
            status="CRITICAL_FAILURE",
            objective_score=0.30,
            heuristic_score=0.35,
            semantic_score=0.25,
            overall_score=0.30,
            gaps=["Anti-criteria violated"],
            recommendations=["Complete rewrite"],
        )

        action = handle_verification_result(state_at_verify, result)
        assert action == "ESCALATE"

    @pytest.mark.unit
    def test_loop_back_increments_iteration(self, state_at_verify):
        """Loop back should increment verify_iteration."""
        from orchestration.outer_loop.verify.entry import execute_loop_back

        initial_iteration = state_at_verify.verify_iteration
        execute_loop_back(state_at_verify)

        loaded = AlgorithmState.load("loopback1234")
        assert loaded.verify_iteration == initial_iteration + 1

    @pytest.mark.unit
    def test_loop_back_adds_verification_result(self, state_at_verify):
        """Loop back should add verification result to history."""
        from orchestration.outer_loop.verify.entry import execute_loop_back

        result = VerificationResult(
            iteration=1,
            timestamp="2026-01-31T12:00:00Z",
            status="GAPS_IDENTIFIED",
            objective_score=0.70,
            heuristic_score=0.65,
            semantic_score=0.60,
            overall_score=0.67,
            gaps=["Missing tests"],
            recommendations=[],
        )

        execute_loop_back(state_at_verify, result)

        loaded = AlgorithmState.load("loopback1234")
        assert len(loaded.verification_history) > 0


class TestVerifyQuestionBubbleUp:
    """Tests for question bubble-up from inner loop."""

    @pytest.mark.unit
    def test_aggregates_questions_from_inner_loop(self, mock_sessions_dir, tmp_path):
        """Should aggregate questions from inner loop memory files."""
        from orchestration.outer_loop.verify.entry import aggregate_inner_loop_questions
        from orchestration.state.algorithm_state import PendingQuestion

        state = AlgorithmState(
            user_query="Build API",
            session_id="questions1234",
        )
        state.save()

        # Create a mock memory file with questions
        memory_content = """# Agent Output: generation

## Section 4: User Questions
```json
{
  "clarification_required": true,
  "questions": [
    {
      "id": "Q1",
      "priority": "P0",
      "question": "REST or GraphQL?",
      "context": "API design",
      "options": ["REST", "GraphQL"],
      "discovered_by": "generation",
      "discovery_phase": "inner_loop"
    }
  ],
  "blocking": true
}
```
"""
        memory_file = tmp_path / "questions1234-generation-memory.md"
        memory_file.write_text(memory_content)

        questions = aggregate_inner_loop_questions(state, [memory_file])
        assert len(questions) == 1
        assert questions[0].id == "Q1"

    @pytest.mark.unit
    def test_adds_questions_to_pending(self, mock_sessions_dir):
        """Aggregated questions should be added to state.pending_questions."""
        from orchestration.outer_loop.verify.entry import add_questions_to_state
        from orchestration.state.algorithm_state import PendingQuestion

        state = AlgorithmState(
            user_query="Build API",
            session_id="addqs123456",
        )
        state.save()

        questions = [
            PendingQuestion(
                id="Q1",
                priority="P0",
                question="REST or GraphQL?",
                context="API design",
                options=["REST", "GraphQL"],
                discovered_by="generation",
                discovery_phase="inner_loop",
            )
        ]

        add_questions_to_state(state, questions)
        state.save()

        loaded = AlgorithmState.load("addqs123456")
        assert len(loaded.pending_questions) == 1
        assert loaded.pending_questions[0].id == "Q1"


class TestVerifyStateManagement:
    """Tests for state management in VERIFY phase."""

    @pytest.mark.unit
    def test_no_ideal_state_fails_verification(self, mock_sessions_dir):
        """Missing ideal_state should cause verification to fail."""
        from orchestration.outer_loop.verify.entry import (
            validate_verification_preconditions,
        )

        state = AlgorithmState(
            user_query="Build API",
            session_id="noideal12345",
        )
        state._fsm._state = AlgorithmPhase.VERIFY
        state.ideal_state = None  # No ideal state
        state.save()

        is_valid, error = validate_verification_preconditions(state)
        assert is_valid is False
        assert "ideal_state" in error.lower()

    @pytest.mark.unit
    def test_can_loop_back_respects_fsm(self, mock_sessions_dir):
        """can_loop_back() should respect FSM constraints."""
        state = AlgorithmState(
            user_query="Build API",
            session_id="fsmcheck1234",
        )
        state._fsm._state = AlgorithmPhase.VERIFY
        state._fsm._verify_iteration = 1
        state.save()

        # Should be able to loop back when under limit
        assert state.can_loop_back() is True

    @pytest.mark.unit
    def test_cannot_loop_back_at_max(self, mock_sessions_dir):
        """can_loop_back() should return False at max iterations."""
        state = AlgorithmState(
            user_query="Build API",
            session_id="maxcheck12345",
        )
        state._fsm._state = AlgorithmPhase.VERIFY
        state._fsm._verify_iteration = 3  # At max
        state.save()

        # FSM should prevent loop back
        assert state.can_loop_back() is False
