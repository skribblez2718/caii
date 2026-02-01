"""
Integration tests for phase sequence transitions.

Tests FSM and State coordination through multi-phase workflows.
Validates state persistence and proper phase sequencing.
"""

import pytest

from orchestration.state.algorithm_state import (
    AlgorithmState,
    IdealState,
    VerificationResult,
)
from orchestration.state.algorithm_fsm import AlgorithmPhase

# ============================================================================
# Helper Functions
# ============================================================================


def progress_to_phase(state: AlgorithmState, target: AlgorithmPhase) -> None:
    """Progress state through phases up to (but not including) target."""
    # Define the standard phase progression
    phase_order = [
        AlgorithmPhase.GATHER,
        AlgorithmPhase.INTERVIEW,
        AlgorithmPhase.INNER_LOOP,
        AlgorithmPhase.VERIFY,
        AlgorithmPhase.LEARN,
    ]

    for phase in phase_order:
        if phase == target:
            break
        state.start_phase(phase)
        state.record_phase_output(phase, {phase.name.lower(): "complete"})


def progress_through_inner_loop(state: AlgorithmState) -> None:
    """Progress through the inner loop phases within INNER_LOOP."""
    # Record outputs for inner loop phases (simulated)
    inner_phases = ["observe", "think", "plan", "build", "execute"]
    for phase_name in inner_phases:
        state.record_phase_output(
            AlgorithmPhase.INNER_LOOP,
            {phase_name: "complete"},
        )


# ============================================================================
# Test Full Phase Sequence (Forward Path)
# ============================================================================


class TestForwardPhaseSequence:
    """Tests for complete forward progression through all phases."""

    @pytest.mark.integration
    def test_full_sequence_initialized_to_gather(self, mock_sessions_dir):
        """State should progress from INITIALIZED to GATHER."""
        state = AlgorithmState(user_query="Build an API")

        assert state.current_phase == AlgorithmPhase.INITIALIZED
        assert state.start_phase(AlgorithmPhase.GATHER)
        assert state.current_phase == AlgorithmPhase.GATHER

    @pytest.mark.integration
    def test_full_sequence_gather_to_ideal_state(self, mock_sessions_dir):
        """State should progress from GATHER to INTERVIEW (ideal state)."""
        state = AlgorithmState(user_query="Build an API")
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "complete"})

        assert state.start_phase(AlgorithmPhase.INTERVIEW)
        assert state.current_phase == AlgorithmPhase.INTERVIEW

    @pytest.mark.integration
    def test_full_sequence_outer_loop(self, mock_sessions_dir):
        """State should complete outer loop: GATHER → INTERVIEW."""
        state = AlgorithmState(user_query="Build an API")

        # GATHER
        assert state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(
            AlgorithmPhase.GATHER, {"johari_schema": {"known": "requirements"}}
        )

        # INTERVIEW
        assert state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(
            AlgorithmPhase.INTERVIEW, {"ideal_state": {"criteria": ["API works"]}}
        )

        # Verify progression
        assert state.phase_outputs.get("GATHER") is not None
        assert state.phase_outputs.get("INTERVIEW") is not None
        assert len(state._fsm._history) >= 3  # INITIALIZED, GATHER, INTERVIEW

    @pytest.mark.integration
    def test_full_sequence_inner_loop(self, mock_sessions_dir):
        """State should progress to INNER_LOOP after INTERVIEW."""
        state = AlgorithmState(user_query="Build an API")

        # Setup: Complete outer loop first
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "done"})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"ideal": "defined"})

        # Progress to INNER_LOOP
        assert state.start_phase(AlgorithmPhase.INNER_LOOP)
        assert state.current_phase == AlgorithmPhase.INNER_LOOP

        # Record inner loop phase outputs
        inner_outputs = {
            "observe": {"observations": "collected"},
            "think": {"analysis": "complete"},
            "plan": {"strategy": "defined"},
            "build": {"artifacts": "created"},
            "execute": {"execution": "complete"},
        }
        for step_name, output in inner_outputs.items():
            state.record_phase_output(AlgorithmPhase.INNER_LOOP, output)

        # Verify inner loop outputs recorded
        assert state.phase_outputs.get("INNER_LOOP") is not None

    @pytest.mark.integration
    def test_full_sequence_through_verification(self, mock_sessions_dir):
        """State should progress through VERIFY phase."""
        state = AlgorithmState(user_query="Build an API")

        # Progress through outer loop and inner loop
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {"step": "done"})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"step": "done"})
        state.start_phase(AlgorithmPhase.INNER_LOOP)
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {"step": "done"})

        # VERIFY
        assert state.start_phase(AlgorithmPhase.VERIFY)
        assert state.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.integration
    def test_full_sequence_to_completion(self, mock_sessions_dir):
        """State should complete full workflow to COMPLETED."""
        state = AlgorithmState(user_query="Build an API")

        # All phases
        phases = [
            AlgorithmPhase.GATHER,
            AlgorithmPhase.INTERVIEW,
            AlgorithmPhase.INNER_LOOP,
            AlgorithmPhase.VERIFY,
        ]
        for phase in phases:
            state.start_phase(phase)
            state.record_phase_output(phase, {phase.name.lower(): "done"})

        # LEARN and complete
        state.start_phase(AlgorithmPhase.LEARN)
        state.record_phase_output(AlgorithmPhase.LEARN, {"learnings": "captured"})

        # Mark completed (requires LEARN phase)
        assert state.current_phase == AlgorithmPhase.LEARN
        state.complete()
        assert state.current_phase == AlgorithmPhase.COMPLETED
        assert state.status == "completed"


# ============================================================================
# Test State Persistence Across Phases
# ============================================================================


class TestStatePersistenceAcrossPhases:
    """Tests for state persistence during phase transitions."""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_state_persists_after_each_phase(self, mock_sessions_dir):
        """State should be loadable after each phase save."""
        session_id = "persist12345"
        state = AlgorithmState(user_query="Test persistence", session_id=session_id)
        state.save()

        # Phase 1: GATHER
        state = AlgorithmState.load(session_id)
        state.start_phase(AlgorithmPhase.GATHER)
        state.save()

        loaded = AlgorithmState.load(session_id)
        assert loaded.current_phase == AlgorithmPhase.GATHER

        # Phase 2: Complete GATHER, start INTERVIEW
        loaded.record_phase_output(AlgorithmPhase.GATHER, {"result": "johari"})
        loaded.start_phase(AlgorithmPhase.INTERVIEW)
        loaded.save()

        reloaded = AlgorithmState.load(session_id)
        assert reloaded.current_phase == AlgorithmPhase.INTERVIEW
        assert reloaded.phase_outputs.get("GATHER") == {"result": "johari"}

    @pytest.mark.integration
    @pytest.mark.critical
    def test_phase_outputs_accumulate_across_saves(self, mock_sessions_dir):
        """Phase outputs should accumulate correctly across save/load cycles."""
        session_id = "accum1234567"
        state = AlgorithmState(user_query="Accumulate test", session_id=session_id)

        phases = [
            AlgorithmPhase.GATHER,
            AlgorithmPhase.INTERVIEW,
            AlgorithmPhase.INNER_LOOP,
        ]
        for phase in phases:
            state.start_phase(phase)
            state.record_phase_output(phase, {"phase": phase.name, "data": f"output"})
            state.save()

            # Reload and verify
            loaded = AlgorithmState.load(session_id)
            assert phase.name in loaded.phase_outputs
            state = loaded  # Continue with loaded state

        # Verify all outputs present
        final = AlgorithmState.load(session_id)
        assert len(final.phase_outputs) == 3
        for phase in phases:
            assert phase.name in final.phase_outputs

    @pytest.mark.integration
    def test_fsm_history_persists(self, mock_sessions_dir):
        """FSM history should persist across save/load."""
        session_id = "history12345"
        state = AlgorithmState(user_query="History test", session_id=session_id)

        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.save()

        loaded = AlgorithmState.load(session_id)

        # History should include: INITIALIZED, GATHER, INTERVIEW
        assert "INITIALIZED" in loaded._fsm._history
        assert "GATHER" in loaded._fsm._history
        assert "INTERVIEW" in loaded._fsm._history

    @pytest.mark.integration
    def test_timestamps_persist(self, mock_sessions_dir):
        """Phase timestamps should persist across save/load."""
        session_id = "timestamps123"
        state = AlgorithmState(user_query="Timestamp test", session_id=session_id)

        state.start_phase(AlgorithmPhase.GATHER)
        state.save()

        loaded = AlgorithmState.load(session_id)

        # start_phase records timestamp with phase name as key
        assert "GATHER" in loaded.phase_timestamps


# ============================================================================
# Test Ideal State Integration
# ============================================================================


class TestIdealStateJohariIntegration:
    """Tests for ideal state integration."""

    @pytest.mark.integration
    def test_johari_then_ideal_state_workflow(self, mock_sessions_dir):
        """Johari (GATHER) and ideal state (INTERVIEW) should integrate correctly."""
        state = AlgorithmState(user_query="Integration test")

        # GATHER phase - set current state
        state.start_phase(AlgorithmPhase.GATHER)
        state.set_current_state(
            domain="CODING",
            state_data={
                "known_knowns": ["Build REST API", "Use Python"],
                "known_unknowns": ["Database choice", "Auth method"],
            },
        )
        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "complete"})

        # INTERVIEW phase - set ideal state
        state.start_phase(AlgorithmPhase.INTERVIEW)
        ideal = IdealState(
            task_id=state.session_id,
            task_type="feature",
            objective="Build a REST API",
            euphoric_surprise="Fast, secure, well-documented API",
            completeness_score=0.95,
        )
        state.set_ideal_state(ideal)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {"ideal_state": "captured"})

        # Verify integration
        assert state.current_state.domain == "CODING"
        assert state.ideal_state is not None
        assert state.ideal_state.completeness_score == 0.95

    @pytest.mark.integration
    def test_ideal_state_refinement_history(self, mock_sessions_dir):
        """Ideal state can be updated."""
        state = AlgorithmState(user_query="Refinement test")

        # Set initial ideal state
        ideal1 = IdealState(
            task_id=state.session_id,
            task_type="feature",
            objective="v1",
            euphoric_surprise="wow",
            completeness_score=0.5,
        )
        state.set_ideal_state(ideal1)
        assert state.ideal_state.objective == "v1"

        # Refine ideal state
        ideal2 = IdealState(
            task_id=state.session_id,
            task_type="feature",
            objective="v2",
            euphoric_surprise="even better wow",
            completeness_score=0.9,
        )
        state.set_ideal_state(ideal2)
        assert state.ideal_state.objective == "v2"
        assert state.ideal_state.completeness_score == 0.9


# ============================================================================
# Test Verification Integration
# ============================================================================


class TestVerificationIntegration:
    """Tests for verification result integration."""

    @pytest.mark.integration
    def test_verification_results_accumulate(self, mock_sessions_dir):
        """Multiple verification results should accumulate."""
        state = AlgorithmState(user_query="Verification test")

        # Add verification results using VerificationResult dataclass
        state.add_verification_result(
            VerificationResult(
                iteration=0,
                timestamp="2026-01-27T10:00:00Z",
                status="VERIFIED",
                objective_score=1.0,
                heuristic_score=1.0,
                semantic_score=1.0,
                overall_score=1.0,
                gaps=[],
                recommendations=[],
            )
        )
        state.add_verification_result(
            VerificationResult(
                iteration=1,
                timestamp="2026-01-27T10:01:00Z",
                status="VERIFIED",
                objective_score=1.0,
                heuristic_score=1.0,
                semantic_score=1.0,
                overall_score=1.0,
                gaps=[],
                recommendations=[],
            )
        )
        state.add_verification_result(
            VerificationResult(
                iteration=2,
                timestamp="2026-01-27T10:02:00Z",
                status="GAPS_IDENTIFIED",
                objective_score=0.7,
                heuristic_score=0.8,
                semantic_score=0.6,
                overall_score=0.7,
                gaps=["coverage below 80%"],
                recommendations=["add more tests"],
            )
        )

        assert len(state.verification_history) == 3
        assert state.verification_history[0].status == "VERIFIED"
        assert state.verification_history[2].status == "GAPS_IDENTIFIED"

    @pytest.mark.integration
    def test_verification_tracks_iteration(self, mock_sessions_dir):
        """Verification results should track iteration count."""
        state = AlgorithmState(user_query="Iteration test")

        # Progress to VERIFY
        state.start_phase(AlgorithmPhase.GATHER)
        state.record_phase_output(AlgorithmPhase.GATHER, {})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.record_phase_output(AlgorithmPhase.INTERVIEW, {})
        state.start_phase(AlgorithmPhase.INNER_LOOP)
        state.record_phase_output(AlgorithmPhase.INNER_LOOP, {})
        state.start_phase(AlgorithmPhase.VERIFY)

        # Add verification result for iteration 0
        state.add_verification_result(
            VerificationResult(
                iteration=0,
                timestamp="2026-01-27T10:00:00Z",
                status="GAPS_IDENTIFIED",
                objective_score=0.5,
                heuristic_score=0.5,
                semantic_score=0.5,
                overall_score=0.5,
                gaps=["first pass failed"],
                recommendations=[],
            )
        )

        # Add verification result for iteration 1
        state.add_verification_result(
            VerificationResult(
                iteration=1,
                timestamp="2026-01-27T10:01:00Z",
                status="VERIFIED",
                objective_score=1.0,
                heuristic_score=1.0,
                semantic_score=1.0,
                overall_score=1.0,
                gaps=[],
                recommendations=[],
            )
        )

        assert state.verification_history[0].iteration == 0
        assert state.verification_history[1].iteration == 1


# ============================================================================
# Test Complexity Persistence
# ============================================================================


class TestComplexityPersistence:
    """Tests for complexity field persistence across phase transitions."""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_complexity_persists_across_phase_transitions(self, mock_sessions_dir):
        """Complexity should be unchanged after GATHER → INTERVIEW."""
        session_id = "cplx_persist1"
        state = AlgorithmState(
            user_query="Test complexity persistence",
            session_id=session_id,
            complexity="moderate",
        )
        state.save()

        # Progress through phases
        state = AlgorithmState.load(session_id)
        assert state.complexity == "moderate"

        state.start_phase(AlgorithmPhase.GATHER)
        state.save()

        state = AlgorithmState.load(session_id)
        assert state.complexity == "moderate"

        state.record_phase_output(AlgorithmPhase.GATHER, {"johari": "done"})
        state.start_phase(AlgorithmPhase.INTERVIEW)
        state.save()

        state = AlgorithmState.load(session_id)
        assert state.complexity == "moderate"

    @pytest.mark.integration
    def test_all_complexity_levels_store_correctly(self, mock_sessions_dir):
        """All 5 complexity levels should persist correctly."""
        categories = ["trivial", "simple", "moderate", "complex", "very_complex"]

        for i, category in enumerate(categories):
            session_id = f"cplx_cat_{i}"
            state = AlgorithmState(
                user_query=f"Test {category}",
                session_id=session_id,
                complexity=category,
            )
            state.save()

            loaded = AlgorithmState.load(session_id)
            assert loaded.complexity == category, f"Failed for category: {category}"

    @pytest.mark.integration
    def test_complexity_persists_through_full_workflow(self, mock_sessions_dir):
        """Complexity should persist through complete workflow."""
        session_id = "cplx_full_wf"
        state = AlgorithmState(
            user_query="Full workflow complexity test",
            session_id=session_id,
            complexity="simple",
        )
        state.save()

        # All phases
        phases = [
            AlgorithmPhase.GATHER,
            AlgorithmPhase.INTERVIEW,
            AlgorithmPhase.INNER_LOOP,
            AlgorithmPhase.VERIFY,
            AlgorithmPhase.LEARN,
        ]
        for phase in phases:
            state = AlgorithmState.load(session_id)
            state.start_phase(phase)
            state.record_phase_output(phase, {phase.name.lower(): "done"})
            state.save()

            # Verify complexity persists
            loaded = AlgorithmState.load(session_id)
            assert loaded.complexity == "simple"

        # Mark completed
        state = AlgorithmState.load(session_id)
        state.complete()
        state.save()

        final = AlgorithmState.load(session_id)
        assert final.complexity == "simple"
        assert final.current_phase == AlgorithmPhase.COMPLETED

    @pytest.mark.integration
    def test_decomposition_properties_persist(self, mock_sessions_dir):
        """decomposition_required should work after load."""
        # Test complex (decomposition required)
        state1 = AlgorithmState(
            user_query="Complex task", session_id="decomp_prop1", complexity="complex"
        )
        state1.save()

        loaded1 = AlgorithmState.load("decomp_prop1")
        assert loaded1.decomposition_required is True

        # Test very_complex (decomposition required)
        state2 = AlgorithmState(
            user_query="Very complex task",
            session_id="decomp_prop2",
            complexity="very_complex",
        )
        state2.save()

        loaded2 = AlgorithmState.load("decomp_prop2")
        assert loaded2.decomposition_required is True

        # Test simple (decomposition not required)
        state3 = AlgorithmState(
            user_query="Simple task", session_id="decomp_prop3", complexity="simple"
        )
        state3.save()

        loaded3 = AlgorithmState.load("decomp_prop3")
        assert loaded3.decomposition_required is False
