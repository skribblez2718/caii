"""
Unit tests for entry_base.py

Tests the entry point factory functions and PhaseConfig dataclass.
Following TDD: These tests are written BEFORE the implementation.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# ============================================================================
# PhaseConfig Tests
# ============================================================================


@pytest.mark.unit
class TestPhaseConfig:
    """Tests for PhaseConfig dataclass."""

    def test_phase_config_creation(self):
        """PhaseConfig should accept all required parameters."""
        from orchestration.entry_base import PhaseConfig

        config = PhaseConfig(
            step_num=1,
            phase_name="OBSERVE",
            content_file="observe_phase.md",
            description="OBSERVE Phase (Step 1)",
        )

        assert config.step_num == 1
        assert config.phase_name == "OBSERVE"
        assert config.content_file == "observe_phase.md"
        assert config.description == "OBSERVE Phase (Step 1)"

    def test_phase_config_immutable(self):
        """PhaseConfig should be immutable (frozen)."""
        from orchestration.entry_base import PhaseConfig

        config = PhaseConfig(
            step_num=1,
            phase_name="OBSERVE",
            content_file="observe_phase.md",
            description="Test",
        )

        with pytest.raises(AttributeError):
            config.step_num = 2  # type: ignore

    def test_phase_config_float_step_num(self):
        """PhaseConfig should support float step numbers (e.g., 0.5)."""
        from orchestration.entry_base import PhaseConfig

        config = PhaseConfig(
            step_num=0.5,
            phase_name="IDEAL_STATE",
            content_file="ideal_state.md",
            description="IDEAL STATE Phase",
        )

        assert config.step_num == 0.5

    def test_phase_config_extra_placeholders_optional(self):
        """PhaseConfig should allow optional extra_placeholders."""
        from orchestration.entry_base import PhaseConfig

        config = PhaseConfig(
            step_num=1,
            phase_name="TEST",
            content_file="test.md",
            description="Test",
        )

        assert config.extra_placeholders is None

    def test_phase_config_with_extra_placeholders(self):
        """PhaseConfig should accept extra_placeholders callable."""
        from orchestration.entry_base import PhaseConfig

        def extra_fn(state: Any) -> Dict[str, Any]:
            return {"task_id": state.session_id}

        config = PhaseConfig(
            step_num=8,
            phase_name="VERIFY",
            content_file="verify.md",
            description="VERIFY Phase",
            extra_placeholders=extra_fn,
        )

        assert config.extra_placeholders is extra_fn


# ============================================================================
# load_state_or_exit Tests
# ============================================================================


@pytest.mark.unit
class TestLoadStateOrExit:
    """Tests for load_state_or_exit function."""

    def test_load_state_success(self, mock_sessions_dir):
        """load_state_or_exit should return state when found."""
        from orchestration.entry_base import load_state_or_exit
        from orchestration.state import AlgorithmState

        # Create and save a state
        state = AlgorithmState(user_query="test query", session_id="test12345678")
        state.save()

        # Load it back
        result = load_state_or_exit("test12345678")

        assert result is not None
        assert result.session_id == "test12345678"
        assert result.user_query == "test query"

    def test_load_state_not_found_exits(self, mock_sessions_dir):
        """load_state_or_exit should exit with code 1 when not found."""
        from orchestration.entry_base import load_state_or_exit

        with pytest.raises(SystemExit) as exc_info:
            load_state_or_exit("nonexistent12")

        assert exc_info.value.code == 1

    def test_load_state_not_found_prints_error(self, mock_sessions_dir, capsys):
        """load_state_or_exit should print error message to stderr."""
        from orchestration.entry_base import load_state_or_exit

        with pytest.raises(SystemExit):
            load_state_or_exit("nonexistent12")

        captured = capsys.readouterr()
        assert "nonexistent12" in captured.err
        assert "not found" in captured.err.lower()


# ============================================================================
# start_phase_or_exit Tests
# ============================================================================


@pytest.mark.unit
class TestStartPhaseOrExit:
    """Tests for start_phase_or_exit function."""

    def test_start_phase_success(self, mock_sessions_dir):
        """start_phase_or_exit should succeed for valid transition."""
        from orchestration.entry_base import start_phase_or_exit
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="test")
        # INITIALIZED -> GATHER is valid
        start_phase_or_exit(state, step_num=0, phase_name="GATHER")

        # Should not raise, and state should be updated
        from orchestration.state.algorithm_fsm import AlgorithmPhase

        assert state.current_phase == AlgorithmPhase.GATHER

    def test_start_phase_invalid_transition_exits(self, mock_sessions_dir):
        """start_phase_or_exit should exit for invalid transition."""
        from orchestration.entry_base import start_phase_or_exit
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="test")
        # INITIALIZED -> OBSERVE is invalid (must go through GATHER first)
        with pytest.raises(SystemExit) as exc_info:
            start_phase_or_exit(state, step_num=1, phase_name="OBSERVE")

        assert exc_info.value.code == 1

    def test_start_phase_invalid_prints_error(self, mock_sessions_dir, capsys):
        """start_phase_or_exit should print error to stderr on failure."""
        from orchestration.entry_base import start_phase_or_exit
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="test")

        with pytest.raises(SystemExit):
            start_phase_or_exit(state, step_num=1, phase_name="OBSERVE")

        captured = capsys.readouterr()
        assert "OBSERVE" in captured.err
        assert "Cannot transition" in captured.err


# ============================================================================
# create_phase_parser Tests
# ============================================================================


@pytest.mark.unit
class TestCreatePhaseParser:
    """Tests for create_phase_parser function."""

    def test_parser_has_state_argument(self):
        """Parser should have required --state argument."""
        from orchestration.entry_base import create_phase_parser

        parser = create_phase_parser("Test Phase")

        # Parse with --state
        args = parser.parse_args(["--state", "abc123"])
        assert args.state == "abc123"

    def test_parser_state_required(self):
        """Parser should require --state argument."""
        from orchestration.entry_base import create_phase_parser

        parser = create_phase_parser("Test Phase")

        with pytest.raises(SystemExit):
            parser.parse_args([])  # Missing --state

    def test_parser_has_optional_user_query(self):
        """Parser should have optional positional user_query."""
        from orchestration.entry_base import create_phase_parser

        parser = create_phase_parser("Test Phase")

        # Parse with user_query
        args = parser.parse_args(["--state", "abc123", "my query"])
        assert args.user_query == "my query"

    def test_parser_user_query_defaults_empty(self):
        """Parser user_query should default to empty string."""
        from orchestration.entry_base import create_phase_parser

        parser = create_phase_parser("Test Phase")

        args = parser.parse_args(["--state", "abc123"])
        assert args.user_query == ""

    def test_parser_uses_description(self):
        """Parser should use provided description."""
        from orchestration.entry_base import create_phase_parser

        parser = create_phase_parser("My Custom Phase (Step 42)")

        assert "My Custom Phase" in parser.description


# ============================================================================
# run_phase_entry Tests
# ============================================================================


@pytest.mark.unit
class TestRunPhaseEntry:
    """Tests for run_phase_entry function."""

    def test_run_phase_entry_loads_state(self, mock_sessions_dir, tmp_path):
        """run_phase_entry should load state from session_id."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        # Create state and save
        state = AlgorithmState(user_query="test query", session_id="session12345")
        state.save()

        # Create mock content file
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        content_file = content_dir / "test_phase.md"
        content_file.write_text("Phase content: {user_query}")

        # Create caller file path
        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test_phase.md",
            description="Test Phase",
        )

        # Mock load_content in orchestration.utils where it's imported from
        with patch("orchestration.utils.load_content") as mock_load:
            mock_load.return_value = "Phase content: {user_query}"

            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "session12345"],
            )

    def test_run_phase_entry_saves_state_before_output(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should save state BEFORE printing output."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        # Create state
        state = AlgorithmState(user_query="test", session_id="savefirst123")
        state.save()

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test.md",
            description="Test",
        )

        save_called_before_print = []

        original_save = AlgorithmState.save

        def tracking_save(self):
            save_called_before_print.append("save")
            original_save(self)

        with patch("orchestration.utils.load_content") as mock_load:
            mock_load.return_value = "Content"
            with patch.object(AlgorithmState, "save", tracking_save):
                run_phase_entry(
                    str(caller_file),
                    config,
                    argv=["--state", "savefirst123"],
                )

        captured = capsys.readouterr()
        # Verify save was called
        assert "save" in save_called_before_print
        # Verify output was printed
        assert "Content" in captured.out

    def test_run_phase_entry_substitutes_placeholders(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should substitute user_query and session_id."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="my special query", session_id="sub12345678")
        state.save()

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test.md",
            description="Test",
        )

        with patch("orchestration.utils.load_content") as mock_load:
            mock_load.return_value = "Query: {user_query}, Session: {session_id}"
            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "sub12345678"],
            )

        captured = capsys.readouterr()
        assert "my special query" in captured.out
        assert "sub12345678" in captured.out

    def test_run_phase_entry_calls_extra_placeholders(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should call extra_placeholders if provided."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="test", session_id="extra1234567")
        state.save()

        caller_file = tmp_path / "entry.py"

        def extra_fn(s):
            return {"custom_field": "custom_value"}

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test.md",
            description="Test",
            extra_placeholders=extra_fn,
        )

        with patch("orchestration.utils.load_content") as mock_load:
            mock_load.return_value = "Custom: {custom_field}"
            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "extra1234567"],
            )

        captured = capsys.readouterr()
        assert "custom_value" in captured.out

    def test_run_phase_entry_exits_on_invalid_state(self, mock_sessions_dir, tmp_path):
        """run_phase_entry should exit if state not found."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test.md",
            description="Test",
        )

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "nonexistent12"],
            )

        assert exc_info.value.code == 1

    def test_run_phase_entry_exits_on_invalid_transition(
        self, mock_sessions_dir, tmp_path
    ):
        """run_phase_entry should exit if phase transition invalid."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="test", session_id="invalid12345")
        state.save()

        caller_file = tmp_path / "entry.py"

        # Try to transition to OBSERVE without going through GATHER first
        config = PhaseConfig(
            step_num=1,  # OBSERVE
            phase_name="OBSERVE",
            content_file="test.md",
            description="Test",
        )

        with pytest.raises(SystemExit) as exc_info:
            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "invalid12345"],
            )

        assert exc_info.value.code == 1


# ============================================================================
# PhaseConfig Agent Flow Tests
# ============================================================================


@pytest.mark.unit
class TestPhaseConfigAgentFlow:
    """Tests for PhaseConfig agent flow support."""

    def test_phase_config_with_agent_flow(self):
        """PhaseConfig should accept agent_flow parameter."""
        from orchestration.entry_base import PhaseConfig
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
        from pathlib import Path

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        config = PhaseConfig(
            step_num=1,
            phase_name="TEST",
            content_file="test.md",
            description="Test Phase",
            agent_flow=flow,
            skill_name="test_skill",
            skill_content_dir=Path("/content"),
        )

        assert config.agent_flow is flow
        assert config.skill_name == "test_skill"
        assert config.skill_content_dir == Path("/content")

    def test_phase_config_agent_flow_defaults_none(self):
        """PhaseConfig agent_flow should default to None."""
        from orchestration.entry_base import PhaseConfig

        config = PhaseConfig(
            step_num=1,
            phase_name="TEST",
            content_file="test.md",
            description="Test",
        )

        assert config.agent_flow is None
        assert config.skill_name is None
        assert config.skill_content_dir is None


# ============================================================================
# run_phase_entry Agent Flow Tests
# ============================================================================


@pytest.mark.unit
class TestRunPhaseEntryAgentFlow:
    """Tests for run_phase_entry agent flow support."""

    def test_run_phase_entry_invokes_agent_flow(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should invoke agent flow when configured."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
        from pathlib import Path

        # Create state
        state = AlgorithmState(user_query="test", session_id="flowtest1234")
        state.save()

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="unused.md",  # Won't be used in flow mode
            description="Test",
            agent_flow=flow,
            skill_name="test",
            skill_content_dir=Path("/content"),
        )

        with patch("orchestration.flow_invoker.invoke_agent_flow") as mock_invoke:
            mock_invoke.return_value = "MANDATORY DIRECTIVE OUTPUT"

            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "flowtest1234"],
            )

            mock_invoke.assert_called_once()
            call_kwargs = mock_invoke.call_args.kwargs
            assert call_kwargs["flow"] is flow
            assert call_kwargs["task_id"] == "flowtest1234"
            assert call_kwargs["skill_name"] == "test"
            assert call_kwargs["phase_id"] == "gather"

        captured = capsys.readouterr()
        assert "MANDATORY DIRECTIVE OUTPUT" in captured.out

    def test_run_phase_entry_prints_flow_header(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should print flow header with agent flow."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
        from pathlib import Path

        state = AlgorithmState(user_query="test", session_id="header123456")
        state.save()

        flow = AgentFlow(
            flow_id="header-flow",
            name="Header Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="research",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="unused.md",
            description="Test",
            agent_flow=flow,
            skill_name="test",
        )

        with patch("orchestration.flow_invoker.invoke_agent_flow") as mock_invoke:
            mock_invoke.return_value = "directive"

            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "header123456"],
            )

        captured = capsys.readouterr()
        assert "GATHER Phase" in captured.out
        assert "header123456" in captured.out
        assert "Header Test Flow" in captured.out
        assert "header-flow" in captured.out

    def test_run_phase_entry_uses_static_content_without_flow(
        self, mock_sessions_dir, tmp_path, capsys
    ):
        """run_phase_entry should use static content when no agent_flow."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState

        state = AlgorithmState(user_query="my query", session_id="static123456")
        state.save()

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="test.md",
            description="Test",
            # No agent_flow
        )

        with patch("orchestration.utils.load_content") as mock_load:
            mock_load.return_value = "Static content: {user_query}"

            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "static123456"],
            )

        captured = capsys.readouterr()
        assert "my query" in captured.out
        # Should not have flow directive output markers
        assert "MANDATORY" not in captured.out

    def test_run_phase_entry_defaults_skill_name_to_phase(
        self, mock_sessions_dir, tmp_path
    ):
        """run_phase_entry should default skill_name to phase_name.lower()."""
        from orchestration.entry_base import PhaseConfig, run_phase_entry
        from orchestration.state import AlgorithmState
        from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern

        state = AlgorithmState(user_query="test", session_id="default12345")
        state.save()

        flow = AgentFlow(
            flow_id="test-flow",
            name="Test Flow",
            source="skill",
            steps=(
                FlowStep(
                    agent_name="analysis",
                    context_pattern=ContextPattern.WORKFLOW_ONLY,
                    predecessors=(),
                ),
            ),
        )

        caller_file = tmp_path / "entry.py"

        config = PhaseConfig(
            step_num=0,
            phase_name="GATHER",
            content_file="unused.md",
            description="Test",
            agent_flow=flow,
            # skill_name not specified - should default to "gather"
        )

        with patch("orchestration.flow_invoker.invoke_agent_flow") as mock_invoke:
            mock_invoke.return_value = "directive"

            run_phase_entry(
                str(caller_file),
                config,
                argv=["--state", "default12345"],
            )

            call_kwargs = mock_invoke.call_args.kwargs
            assert call_kwargs["skill_name"] == "gather"
