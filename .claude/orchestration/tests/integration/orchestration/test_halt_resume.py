"""
Integration tests for halt and resume workflows.

Tests clarification flow, halt persistence, and resume from various phases.
"""

import pytest

# ============================================================================
# Test Halt from Various Phases
# ============================================================================


class TestHaltFromPhases:
    """Tests for halting execution from different phases."""

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_halt_from_gather_phase(self, mock_sessions_dir):
        """Should be able to halt from GATHER phase."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Ambiguous request")
        state.start_phase(0)  # GATHER

        result = state.halt_for_clarification(
            reason="Requirements unclear",
            questions=["What database should we use?", "REST or GraphQL?"],
        )

        assert result is True
        assert state.current_phase == AlgorithmPhase.HALTED
        assert state.status == "halted"
        assert len(state.clarification_questions) == 2

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_halt_from_plan_phase(self, mock_sessions_dir):
        """Should be able to halt from PLAN phase."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to PLAN phase
        for step in [0, 0.5, 1, 2]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(3)  # PLAN

        result = state.halt_for_clarification(
            reason="Architecture decision needed",
            questions=["Monolith or microservices?"],
        )

        assert result is True
        assert state.current_phase == AlgorithmPhase.HALTED
        assert state.halt_reason == "Architecture decision needed"

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_halt_from_execute_phase(self, mock_sessions_dir):
        """Should be able to halt from EXECUTE phase."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Deploy application")

        # Progress to EXECUTE phase
        for step in [0, 0.5, 1, 2, 3, 4]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(5)  # EXECUTE

        result = state.halt_for_clarification(
            reason="External credentials needed",
            questions=["AWS access key?", "Deploy to staging or prod?"],
        )

        assert result is True
        assert state.current_phase == AlgorithmPhase.HALTED


# ============================================================================
# Test Resume Scenarios
# ============================================================================


class TestResumeScenarios:
    """Tests for resuming from halt state."""

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_resume_to_gather(self, mock_sessions_dir):
        """Should resume to GATHER phase from halt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")
        state.halt_for_clarification("Need info", ["Question?"])

        result = state.resume_from_halt(
            target_step=0, clarification_response={"answer": "PostgreSQL"}
        )

        assert result is True
        assert state.current_phase == AlgorithmPhase.GATHER
        assert state.status == "in_progress"
        assert state.halt_reason is None

    @pytest.mark.integration
    @pytest.mark.fsm
    def test_resume_to_mid_workflow_phase(self, mock_sessions_dir):
        """Should resume to middle of workflow from halt."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build API")

        # Progress to PLAN, then halt
        for step in [0, 0.5, 1, 2]:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(3)  # PLAN
        state.halt_for_clarification("Need architecture decision", ["Microservices?"])

        # Resume to THINK (step 2) for re-analysis
        result = state.resume_from_halt(
            target_step=2, clarification_response={"architecture": "monolith"}
        )

        assert result is True
        assert state.current_phase == AlgorithmPhase.THINK

    @pytest.mark.integration
    def test_resume_stores_clarification_response(self, mock_sessions_dir):
        """Resume should store clarification response in metadata."""
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(user_query="Build API")
        state.halt_for_clarification("Need info", ["Q1", "Q2"])

        clarification = {
            "Q1": "Answer 1",
            "Q2": "Answer 2",
            "timestamp": "2026-01-27T10:00:00Z",
        }

        state.resume_from_halt(target_step=0, clarification_response=clarification)

        assert state.metadata["last_clarification"] == clarification


# ============================================================================
# Test Halt Persistence
# ============================================================================


class TestHaltPersistence:
    """Tests for halt state persistence."""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_halt_state_persists(self, mock_sessions_dir):
        """Halt state should persist across save/load."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "halt12345678"
        state = AlgorithmState(
            user_query="Test halt persistence", session_id=session_id
        )

        state.halt_for_clarification(
            reason="Need database selection",
            questions=["PostgreSQL or MySQL?", "ORM framework?"],
        )
        state.save()

        # Load and verify halt state persists
        loaded = AlgorithmState.load(session_id)

        assert loaded.current_phase == AlgorithmPhase.HALTED
        assert loaded.status == "halted"
        assert loaded.halt_reason == "Need database selection"
        assert loaded.clarification_questions == [
            "PostgreSQL or MySQL?",
            "ORM framework?",
        ]

    @pytest.mark.integration
    @pytest.mark.critical
    def test_resume_state_persists(self, mock_sessions_dir):
        """Resume state should persist including clarification response."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "resume1234567"
        state = AlgorithmState(
            user_query="Test resume persistence", session_id=session_id
        )

        state.halt_for_clarification("Need info", ["Question?"])
        state.save()

        # Load, resume, save
        loaded = AlgorithmState.load(session_id)
        loaded.resume_from_halt(
            target_step=0, clarification_response={"database": "PostgreSQL"}
        )
        loaded.save()

        # Reload and verify resume persisted
        final = AlgorithmState.load(session_id)

        assert final.current_phase == AlgorithmPhase.GATHER
        assert final.status == "in_progress"
        assert final.halt_reason is None
        assert final.clarification_questions == []
        assert final.metadata["last_clarification"]["database"] == "PostgreSQL"


# ============================================================================
# Test Halt/Resume with Phase Progress
# ============================================================================


class TestHaltResumeWithProgress:
    """Tests for halt/resume scenarios that preserve phase progress."""

    @pytest.mark.integration
    def test_halt_preserves_completed_phases(self, mock_sessions_dir):
        """Halt should preserve outputs from completed phases."""
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(user_query="Build API")

        # Complete some phases
        state.start_phase(0)
        state.complete_phase(0, {"johari": "discovered"})
        state.start_phase(0.5)
        state.complete_phase(0.5, {"ideal": "captured"})
        state.start_phase(1)
        state.complete_phase(1, {"observed": "state"})

        # Halt in THINK phase
        state.start_phase(2)
        state.halt_for_clarification("Need more context", ["Details?"])

        # Verify completed phases preserved
        assert state.phase_outputs.get("0") == {"johari": "discovered"}
        assert state.phase_outputs.get("0.5") == {"ideal": "captured"}
        assert state.phase_outputs.get("1") == {"observed": "state"}

    @pytest.mark.integration
    def test_resume_continues_from_preserved_state(self, mock_sessions_dir):
        """Resume should continue with preserved phase outputs."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "continue12345"
        state = AlgorithmState(user_query="Build API", session_id=session_id)

        # Complete some phases
        state.start_phase(0)
        state.complete_phase(0, {"johari": "discovered"})
        state.start_phase(0.5)
        state.complete_phase(0.5, {"ideal": "captured"})

        # Halt
        state.start_phase(1)
        state.halt_for_clarification("Need info", ["Question?"])
        state.save()

        # Load and resume
        loaded = AlgorithmState.load(session_id)
        loaded.resume_from_halt(target_step=1, clarification_response={"answer": "yes"})

        # Continue workflow
        assert loaded.current_phase == AlgorithmPhase.OBSERVE
        assert loaded.phase_outputs.get("0") == {"johari": "discovered"}
        assert loaded.phase_outputs.get("0.5") == {"ideal": "captured"}

        # Can continue to next phase
        loaded.complete_phase(1, {"observations": "with clarification"})
        assert loaded.start_phase(2)
        assert loaded.current_phase == AlgorithmPhase.THINK


# ============================================================================
# Test Multiple Halt/Resume Cycles
# ============================================================================


class TestMultipleHaltResumeCycles:
    """Tests for multiple halt/resume cycles in a single workflow."""

    @pytest.mark.integration
    def test_multiple_halt_resume_cycles(self, mock_sessions_dir):
        """Should support multiple halt/resume cycles."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "multicycle123"
        state = AlgorithmState(user_query="Complex project", session_id=session_id)

        # First cycle: halt during GATHER
        state.start_phase(0)
        state.halt_for_clarification("Need requirements", ["Scope?"])
        state.save()

        loaded = AlgorithmState.load(session_id)
        loaded.resume_from_halt(
            target_step=0, clarification_response={"scope": "MVP only"}
        )
        loaded.complete_phase(0, {"johari": "done"})
        loaded.save()

        # Second cycle: halt during IDEAL_STATE
        loaded = AlgorithmState.load(session_id)
        loaded.start_phase(0.5)
        loaded.halt_for_clarification("Need success criteria", ["What metrics?"])
        loaded.save()

        loaded = AlgorithmState.load(session_id)
        loaded.resume_from_halt(
            target_step=0.5, clarification_response={"metrics": "latency < 100ms"}
        )
        loaded.complete_phase(0.5, {"ideal": "defined"})
        loaded.save()

        # Verify final state
        final = AlgorithmState.load(session_id)
        assert final.current_phase == AlgorithmPhase.IDEAL_STATE
        assert final.phase_outputs.get("0") == {"johari": "done"}
        assert final.phase_outputs.get("0.5") == {"ideal": "defined"}
        # Should have multiple clarifications in history
        assert "last_clarification" in final.metadata
