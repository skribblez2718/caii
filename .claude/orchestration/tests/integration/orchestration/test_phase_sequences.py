"""
Integration tests for phase sequence transitions.

Tests FSM and State coordination through multi-phase workflows.
Validates state persistence and proper phase sequencing.
"""

import pytest

# ============================================================================
# Test Full Phase Sequence (Forward Path)
# ============================================================================


class TestForwardPhaseSequence:
    """Tests for complete forward progression through all phases."""

    @pytest.mark.integration
    def test_full_sequence_initialized_to_gather(self, mock_sessions_dir):
        """State should progress from INITIALIZED to GATHER."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")

        assert state.current_phase == AlgorithmPhase.INITIALIZED
        assert state.start_phase(0)  # GATHER
        assert state.current_phase == AlgorithmPhase.GATHER

    @pytest.mark.integration
    def test_full_sequence_gather_to_ideal_state(self, mock_sessions_dir):
        """State should progress from GATHER to IDEAL_STATE."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")
        state.start_phase(0)  # GATHER
        state.complete_phase(0, {"johari": "complete"})

        assert state.start_phase(0.5)  # IDEAL_STATE
        assert state.current_phase == AlgorithmPhase.IDEAL_STATE

    @pytest.mark.integration
    def test_full_sequence_outer_loop(self, mock_sessions_dir):
        """State should complete outer loop: GATHER → IDEAL_STATE."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")

        # GATHER (Step 0)
        assert state.start_phase(0)
        state.complete_phase(0, {"johari_schema": {"known": "requirements"}})

        # IDEAL_STATE (Step 0.5)
        assert state.start_phase(0.5)
        state.complete_phase(0.5, {"ideal_state": {"criteria": ["API works"]}})

        # Verify progression
        assert state.phase_outputs.get("0") is not None
        assert state.phase_outputs.get("0.5") is not None
        assert len(state.fsm.history) >= 3  # INITIALIZED, GATHER, IDEAL_STATE

    @pytest.mark.integration
    def test_full_sequence_inner_loop(self, mock_sessions_dir):
        """State should complete inner loop: OBSERVE → THINK → PLAN → BUILD → EXECUTE."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")

        # Setup: Complete outer loop first
        state.start_phase(0)
        state.complete_phase(0, {"johari": "done"})
        state.start_phase(0.5)
        state.complete_phase(0.5, {"ideal": "defined"})

        # Inner loop phases
        inner_phases = [
            (1, "OBSERVE", {"observations": "collected"}),
            (2, "THINK", {"analysis": "complete"}),
            (3, "PLAN", {"strategy": "defined"}),
            (4, "BUILD", {"artifacts": "created"}),
            (5, "EXECUTE", {"execution": "complete"}),
        ]

        for step, name, output in inner_phases:
            assert state.start_phase(step), f"Failed to start {name}"
            state.complete_phase(step, output)

        # Verify all inner loop phases completed
        for step, name, _ in inner_phases:
            assert str(step) in state.phase_outputs, f"Missing output for {name}"

    @pytest.mark.integration
    def test_full_sequence_through_verification(self, mock_sessions_dir):
        """State should progress through VERIFY phase."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")

        # Fast-forward through all phases to VERIFY
        phases = [0, 0.5, 1, 2, 3, 4, 5]
        for step in phases:
            state.start_phase(step)
            state.complete_phase(step, {f"step_{step}": "done"})

        # VERIFY (Step 8)
        assert state.start_phase(8)
        assert state.current_phase == AlgorithmPhase.VERIFY

    @pytest.mark.integration
    def test_full_sequence_to_completion(self, mock_sessions_dir):
        """State should complete full workflow to COMPLETED."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Build an API")

        # All phases including VERIFY and LEARN
        phases = [0, 0.5, 1, 2, 3, 4, 5, 8, 8.5]
        for step in phases:
            state.start_phase(step)
            state.complete_phase(step, {f"step_{step}": "done"})

        # Mark completed (requires LEARN phase)
        assert state.current_phase == AlgorithmPhase.LEARN
        assert state.mark_completed()
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
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "persist12345"
        state = AlgorithmState(user_query="Test persistence", session_id=session_id)
        state.save()

        # Phase 1: GATHER
        state = AlgorithmState.load(session_id)
        state.start_phase(0)
        state.save()

        loaded = AlgorithmState.load(session_id)
        assert loaded.current_phase == AlgorithmPhase.GATHER

        # Phase 2: Complete GATHER, start IDEAL_STATE
        loaded.complete_phase(0, {"result": "johari"})
        loaded.start_phase(0.5)
        loaded.save()

        reloaded = AlgorithmState.load(session_id)
        assert reloaded.current_phase == AlgorithmPhase.IDEAL_STATE
        assert reloaded.phase_outputs.get("0") == {"result": "johari"}

    @pytest.mark.integration
    @pytest.mark.critical
    def test_phase_outputs_accumulate_across_saves(self, mock_sessions_dir):
        """Phase outputs should accumulate correctly across save/load cycles."""
        from orchestration.state.algorithm_state import AlgorithmState

        session_id = "accum1234567"
        state = AlgorithmState(user_query="Accumulate test", session_id=session_id)

        phases = [0, 0.5, 1, 2, 3]
        for step in phases:
            state.start_phase(step)
            state.complete_phase(step, {"step": step, "data": f"output_{step}"})
            state.save()

            # Reload and verify
            loaded = AlgorithmState.load(session_id)
            assert str(step) in loaded.phase_outputs
            state = loaded  # Continue with loaded state

        # Verify all outputs present
        final = AlgorithmState.load(session_id)
        assert len(final.phase_outputs) == 5
        for step in phases:
            assert str(step) in final.phase_outputs

    @pytest.mark.integration
    def test_fsm_history_persists(self, mock_sessions_dir):
        """FSM history should persist across save/load."""
        from orchestration.state.algorithm_state import AlgorithmState

        session_id = "history12345"
        state = AlgorithmState(user_query="History test", session_id=session_id)

        state.start_phase(0)
        state.complete_phase(0, {})
        state.start_phase(0.5)
        state.save()

        loaded = AlgorithmState.load(session_id)

        # History should include: INITIALIZED, GATHER, IDEAL_STATE
        assert "INITIALIZED" in loaded.fsm.history
        assert "GATHER" in loaded.fsm.history
        assert "IDEAL_STATE" in loaded.fsm.history

    @pytest.mark.integration
    def test_timestamps_persist(self, mock_sessions_dir):
        """Phase timestamps should persist across save/load."""
        from orchestration.state.algorithm_state import AlgorithmState

        session_id = "timestamps123"
        state = AlgorithmState(user_query="Timestamp test", session_id=session_id)

        state.start_phase(0)
        state.complete_phase(0, {})
        state.save()

        loaded = AlgorithmState.load(session_id)

        assert "0" in loaded.phase_timestamps
        assert "started_at" in loaded.phase_timestamps["0"]
        assert "completed_at" in loaded.phase_timestamps["0"]


# ============================================================================
# Test Ideal State and Johari Integration
# ============================================================================


class TestIdealStateJohariIntegration:
    """Tests for ideal state and Johari schema integration."""

    @pytest.mark.integration
    def test_johari_then_ideal_state_workflow(self, mock_sessions_dir):
        """Johari and ideal state should integrate correctly."""
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(user_query="Integration test")

        # GATHER phase - Johari discovery
        state.start_phase(0)
        johari_result = {
            "known_knowns": ["Build REST API", "Use Python"],
            "known_unknowns": ["Database choice", "Auth method"],
            "unknown_knowns": [],
            "unknown_unknowns": [],
        }
        state.update_johari_schema(johari_result)
        state.complete_phase(0, {"johari": johari_result})

        # IDEAL_STATE phase
        state.start_phase(0.5)
        ideal = {
            "success_criteria": [
                "API responds to GET/POST",
                "Authentication works",
            ],
            "anti_criteria": ["No SQL injection", "No exposed secrets"],
        }
        state.update_ideal_state(ideal, completeness_score=0.95)
        state.complete_phase(0.5, {"ideal_state": ideal})

        # Verify integration
        assert state.johari_schema["known_knowns"] == ["Build REST API", "Use Python"]
        assert state.ideal_state["success_criteria"] is not None
        assert state.ideal_state["completeness_score"] == 0.95

    @pytest.mark.integration
    def test_ideal_state_refinement_history(self, mock_sessions_dir):
        """Ideal state refinements should be tracked in history."""
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(user_query="Refinement test")

        # Initial ideal state
        state.update_ideal_state({"version": 1, "criteria": ["basic"]})

        # Refinement 1
        state.update_ideal_state({"version": 2, "criteria": ["enhanced"]})

        # Refinement 2
        state.update_ideal_state({"version": 3, "criteria": ["final"]})

        # Verify history
        assert state.ideal_state_iteration == 3
        assert len(state.ideal_state_history) == 2
        assert state.ideal_state_history[0]["ideal_state"]["version"] == 1
        assert state.ideal_state_history[1]["ideal_state"]["version"] == 2
        assert state.ideal_state["version"] == 3


# ============================================================================
# Test Verification Integration
# ============================================================================


class TestVerificationIntegration:
    """Tests for verification result integration."""

    @pytest.mark.integration
    def test_verification_results_accumulate(self, mock_sessions_dir):
        """Multiple verification results should accumulate."""
        from orchestration.state.algorithm_state import AlgorithmState

        state = AlgorithmState(user_query="Verification test")

        # Simulate multiple verification passes
        state.add_verification_result(
            {"check": "syntax", "details": "all files valid"}, passed=True
        )
        state.add_verification_result(
            {"check": "tests", "details": "3 passing"}, passed=True
        )
        state.add_verification_result(
            {"check": "coverage", "details": "below 80%"}, passed=False
        )

        assert len(state.verification_results) == 3
        assert state.verification_results[0]["passed"] is True
        assert state.verification_results[2]["passed"] is False

    @pytest.mark.integration
    def test_verification_tracks_iteration(self, mock_sessions_dir):
        """Verification results should track iteration count."""
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        state = AlgorithmState(user_query="Iteration test")

        # Fast-forward to VERIFY
        phases = [0, 0.5, 1, 2, 3, 4, 5]
        for step in phases:
            state.start_phase(step)
            state.complete_phase(step, {})

        state.start_phase(8)  # VERIFY

        # Add verification result (iteration 0)
        state.add_verification_result({"check": "first"}, passed=False)

        # Simulate loop-back (increment iteration)
        state.fsm._iteration_count = 1

        # Add verification result (iteration 1)
        state.add_verification_result({"check": "second"}, passed=True)

        assert state.verification_results[0]["iteration"] == 0
        assert state.verification_results[1]["iteration"] == 1


# ============================================================================
# Test Complexity Persistence
# ============================================================================


class TestComplexityPersistence:
    """Tests for complexity field persistence across phase transitions."""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_complexity_persists_across_phase_transitions(self, mock_sessions_dir):
        """Complexity should be unchanged after GATHER → IDEAL_STATE."""
        from orchestration.state.algorithm_state import AlgorithmState

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

        state.start_phase(0)  # GATHER
        state.save()

        state = AlgorithmState.load(session_id)
        assert state.complexity == "moderate"

        state.complete_phase(0, {"johari": "done"})
        state.start_phase(0.5)  # IDEAL_STATE
        state.save()

        state = AlgorithmState.load(session_id)
        assert state.complexity == "moderate"

    @pytest.mark.integration
    def test_all_complexity_levels_store_correctly(self, mock_sessions_dir):
        """All 5 complexity levels should persist correctly."""
        from orchestration.state.algorithm_state import AlgorithmState

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
        from orchestration.state.algorithm_state import AlgorithmState
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        session_id = "cplx_full_wf"
        state = AlgorithmState(
            user_query="Full workflow complexity test",
            session_id=session_id,
            complexity="simple",
        )
        state.save()

        # All phases including VERIFY and LEARN
        phases = [0, 0.5, 1, 2, 3, 4, 5, 8, 8.5]
        for step in phases:
            state = AlgorithmState.load(session_id)
            state.start_phase(step)
            state.complete_phase(step, {f"step_{step}": "done"})
            state.save()

            # Verify complexity persists
            loaded = AlgorithmState.load(session_id)
            assert loaded.complexity == "simple"

        # Mark completed
        state = AlgorithmState.load(session_id)
        state.mark_completed()
        state.save()

        final = AlgorithmState.load(session_id)
        assert final.complexity == "simple"
        assert final.current_phase == AlgorithmPhase.COMPLETED

    @pytest.mark.integration
    def test_decomposition_properties_persist(self, mock_sessions_dir):
        """decomposition_recommended and decomposition_required should work after load."""
        from orchestration.state.algorithm_state import AlgorithmState

        # Test complex (recommended but not required)
        state1 = AlgorithmState(
            user_query="Complex task", session_id="decomp_prop1", complexity="complex"
        )
        state1.save()

        loaded1 = AlgorithmState.load("decomp_prop1")
        assert loaded1.decomposition_recommended is True
        assert loaded1.decomposition_required is False

        # Test very_complex (both recommended and required)
        state2 = AlgorithmState(
            user_query="Very complex task",
            session_id="decomp_prop2",
            complexity="very_complex",
        )
        state2.save()

        loaded2 = AlgorithmState.load("decomp_prop2")
        assert loaded2.decomposition_recommended is True
        assert loaded2.decomposition_required is True
