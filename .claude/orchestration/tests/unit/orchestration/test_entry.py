"""
Unit tests for entry.py

Tests the global orchestration entry point functions:
- extract_complexity
- print_complexity_prompt
- route_based_on_complexity
- main
"""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

# ============================================================================
# TestExtractComplexity
# ============================================================================


class TestExtractComplexity:
    """Tests for extract_complexity() function with 5 METR categories."""

    @pytest.mark.unit
    def test_returns_trivial_for_trivial_response(self):
        """Should return 'trivial' when response contains 'trivial'."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("trivial")

        assert result == "trivial"

    @pytest.mark.unit
    def test_returns_simple_for_simple_response(self):
        """Should return 'simple' when response contains 'simple'."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("simple")

        assert result == "simple"

    @pytest.mark.unit
    def test_returns_moderate_for_moderate_response(self):
        """Should return 'moderate' when response contains 'moderate'."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("moderate")

        assert result == "moderate"

    @pytest.mark.unit
    def test_returns_complex_for_complex_response(self):
        """Should return 'complex' when response contains 'complex'."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("complex")

        assert result == "complex"

    @pytest.mark.unit
    def test_returns_very_complex_for_very_complex_response(self):
        """Should return 'very_complex' when response contains 'very complex'."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("very complex")

        assert result == "very_complex"

    @pytest.mark.unit
    def test_returns_unknown_for_unrecognized(self):
        """Should return 'unknown' for unrecognized response."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("I don't understand")

        assert result == "unknown"

    @pytest.mark.unit
    def test_prioritizes_very_complex_over_complex(self):
        """Should return 'very_complex' if both 'very complex' and 'complex' appear."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("very complex task")

        assert result == "very_complex"

    @pytest.mark.unit
    def test_prioritizes_complex_over_moderate(self):
        """Should return 'complex' if both appear."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("This is complex and moderate in nature")

        assert result == "complex"

    @pytest.mark.unit
    def test_prioritizes_moderate_over_simple(self):
        """Should return 'moderate' if both appear."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("moderate or simple task")

        assert result == "moderate"

    @pytest.mark.unit
    def test_prioritizes_simple_over_trivial(self):
        """Should return 'simple' if both appear."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("simple, not trivial")

        assert result == "simple"

    @pytest.mark.unit
    def test_case_insensitive_all_categories(self):
        """Should be case insensitive for all categories."""
        from orchestration.entry import extract_complexity

        assert extract_complexity("TRIVIAL") == "trivial"
        assert extract_complexity("SIMPLE") == "simple"
        assert extract_complexity("MODERATE") == "moderate"
        assert extract_complexity("COMPLEX") == "complex"
        assert extract_complexity("VERY COMPLEX") == "very_complex"

    @pytest.mark.unit
    def test_handles_hyphen_variants(self):
        """Should detect 'very-complex' with hyphen."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("very-complex")

        assert result == "very_complex"

    @pytest.mark.unit
    def test_handles_underscore_variants(self):
        """Should detect 'very_complex' with underscore."""
        from orchestration.entry import extract_complexity

        result = extract_complexity("very_complex")

        assert result == "very_complex"

    @pytest.mark.unit
    def test_handles_embedded_in_sentence(self):
        """Should detect keywords embedded in longer text."""
        from orchestration.entry import extract_complexity

        result = extract_complexity(
            "After analysis, I classify this task as moderate because..."
        )

        assert result == "moderate"

    @pytest.mark.unit
    def test_handles_embedded_simple(self):
        """Should detect 'simple' embedded in longer text."""
        from orchestration.entry import extract_complexity

        result = extract_complexity(
            "This is a simple task that requires minimal effort."
        )

        assert result == "simple"


# ============================================================================
# TestPrintComplexityPrompt
# ============================================================================


class TestPrintComplexityPrompt:
    """Tests for print_complexity_prompt() function."""

    @pytest.mark.unit
    def test_loads_and_prints_content(self, tmp_path, monkeypatch, capsys):
        """Should load content file and print prompt."""
        from orchestration import entry
        from orchestration import utils

        # Create mock content file
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        content_file = content_dir / "complexity_assessment.md"
        content_file.write_text("Analyze: {user_query}")

        # Mock get_content_dir to return our tmp dir
        def mock_get_content_dir(script_path):
            return content_dir

        monkeypatch.setattr(utils, "get_content_dir", mock_get_content_dir)

        # Reload the load_content function to use our mock
        def mock_load_content(script_path, filename):
            return (content_dir / filename).read_text()

        monkeypatch.setattr(entry, "load_content", mock_load_content)

        entry.print_complexity_prompt("Build an API")

        captured = capsys.readouterr()
        assert "Analyze: Build an API" in captured.out

    @pytest.mark.unit
    def test_substitutes_user_query(self, tmp_path, monkeypatch, capsys):
        """Should substitute {user_query} placeholder."""
        from orchestration import entry

        monkeypatch.setattr(
            entry,
            "load_content",
            lambda *args: "Query: {user_query}",
        )

        entry.print_complexity_prompt("My test query")

        captured = capsys.readouterr()
        assert "Query: My test query" in captured.out


# ============================================================================
# TestRouteBasedOnComplexity
# ============================================================================


class TestRouteBasedOnComplexity:
    """Tests for route_based_on_complexity() function with 5 METR categories."""

    @pytest.mark.unit
    def test_trivial_does_not_create_state(self, mock_sessions_dir, capsys):
        """Trivial route should not create algorithm state."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("trivial", "Simple query")

        captured = capsys.readouterr()
        assert "DA Direct Execution" in captured.out
        assert "MANDATORY" not in captured.out

        # Verify no state file was created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 0

    @pytest.mark.unit
    def test_simple_creates_state_routes_gather(self, mock_sessions_dir, capsys):
        """Simple route should create state and route to GATHER."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("simple", "Simple query with some dependencies")

        captured = capsys.readouterr()
        assert "Last Algorithm" in captured.out
        assert "SIMPLE" in captured.out
        assert "MANDATORY" in captured.out
        assert "gather" in captured.out.lower()
        assert "--state" in captured.out

        # Check state file was created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_moderate_creates_state_routes_gather(self, mock_sessions_dir, capsys):
        """Moderate route should create state and route to GATHER."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("moderate", "Moderate complexity task")

        captured = capsys.readouterr()
        assert "Last Algorithm" in captured.out
        assert "MODERATE" in captured.out
        assert "MANDATORY" in captured.out
        assert "gather" in captured.out.lower()

        # Check state file was created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_complex_creates_state_routes_decompose(self, mock_sessions_dir, capsys):
        """Complex route should create state and route to DECOMPOSE."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("complex", "Complex task requiring decomposition")

        captured = capsys.readouterr()
        assert "DECOMPOSE" in captured.out
        assert "COMPLEX" in captured.out
        assert "MANDATORY" in captured.out
        assert "decompose" in captured.out.lower()
        assert "--state" in captured.out

        # Check state file was created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_very_complex_creates_state_routes_decompose(
        self, mock_sessions_dir, capsys
    ):
        """Very complex route should create state and route to DECOMPOSE."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("very complex", "System-wide refactoring task")

        captured = capsys.readouterr()
        assert "DECOMPOSE" in captured.out
        assert "VERY COMPLEX" in captured.out
        assert "MANDATORY" in captured.out
        assert "decompose" in captured.out.lower()

        # Check state file was created
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_state_includes_complexity_field(self, mock_sessions_dir):
        """Created state should include complexity field."""
        import json

        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("moderate", "Task for complexity test")

        # Read the state file
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

        with open(session_files[0], "r", encoding="utf-8") as f:
            state_data = json.load(f)

        assert "complexity" in state_data
        assert state_data["complexity"] == "moderate"

    @pytest.mark.unit
    @pytest.mark.critical
    def test_simple_saves_before_print(self, mock_sessions_dir, capsys):
        """Simple route should save state BEFORE printing directive."""
        from orchestration.entry import route_based_on_complexity
        from orchestration.state import algorithm_state as state_module

        save_called = []
        print_called = []

        original_save = state_module.AlgorithmState.save

        def tracking_save(self):
            save_called.append(len(print_called))
            return original_save(self)

        with patch.object(state_module.AlgorithmState, "save", tracking_save):
            route_based_on_complexity("simple", "Test query")
            captured = capsys.readouterr()
            print_called.append(True)

        # Save should be called before any output containing MANDATORY
        assert len(save_called) > 0

    @pytest.mark.unit
    def test_unknown_defaults_to_moderate(self, mock_sessions_dir, capsys):
        """Unknown complexity should default to moderate for safety."""
        from orchestration.entry import route_based_on_complexity

        route_based_on_complexity("gibberish", "Some query")

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "Could not determine complexity" in captured.out
        # Should still create state (defaults to moderate)
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1


# ============================================================================
# TestMain
# ============================================================================


class TestMain:
    """Tests for main() function."""

    @pytest.mark.unit
    def test_exits_without_args(self, monkeypatch, capsys):
        """Should exit with error when no arguments provided."""
        from orchestration.entry import main

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        # argparse uses exit code 2 for argument errors
        assert exc_info.value.code in (1, 2)
        captured = capsys.readouterr()
        assert "usage" in captured.err.lower() or "required" in captured.err.lower()

    @pytest.mark.unit
    def test_prints_complexity_prompt_with_query(self, monkeypatch, capsys):
        """Should print complexity prompt with user query."""
        from orchestration import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "Build an API"])
        monkeypatch.setattr(
            entry,
            "load_content",
            lambda *args: "Analyze: {user_query}",
        )

        main_result = entry.main()

        captured = capsys.readouterr()
        assert "Analyze: Build an API" in captured.out

    @pytest.mark.unit
    def test_complexity_arg_triggers_routing(
        self, monkeypatch, mock_sessions_dir, capsys
    ):
        """Should route when --complexity arg provided."""
        from orchestration import entry

        monkeypatch.setattr(
            sys, "argv", ["entry.py", "Build an API", "--complexity", "moderate"]
        )

        entry.main()

        captured = capsys.readouterr()
        # Should route to The Last Algorithm, not print complexity prompt
        assert "Last Algorithm" in captured.out
        assert "MODERATE" in captured.out
        assert "MANDATORY" in captured.out
        # Should have created state
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_complexity_arg_trivial_routes_direct(
        self, monkeypatch, mock_sessions_dir, capsys
    ):
        """Should route to DA direct execution when complexity is trivial."""
        from orchestration import entry

        monkeypatch.setattr(
            sys, "argv", ["entry.py", "Fix typo", "--complexity", "trivial"]
        )

        entry.main()

        captured = capsys.readouterr()
        assert "DA Direct Execution" in captured.out
        assert "TRIVIAL" in captured.out
        # Should NOT create state for trivial
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 0

    @pytest.mark.unit
    def test_complexity_arg_complex_routes_decompose(
        self, monkeypatch, mock_sessions_dir, capsys
    ):
        """Should route to DECOMPOSE when complexity is complex."""
        from orchestration import entry

        monkeypatch.setattr(
            sys, "argv", ["entry.py", "Refactor auth", "--complexity", "complex"]
        )

        entry.main()

        captured = capsys.readouterr()
        assert "DECOMPOSE" in captured.out
        assert "COMPLEX" in captured.out
        assert "MANDATORY" in captured.out
        # Should have created state
        session_files = list(mock_sessions_dir.glob("algorithm-*.json"))
        assert len(session_files) == 1

    @pytest.mark.unit
    def test_no_complexity_arg_prints_prompt(self, monkeypatch, capsys):
        """Should print complexity prompt when no --complexity arg."""
        from orchestration import entry

        monkeypatch.setattr(sys, "argv", ["entry.py", "Build an API"])
        monkeypatch.setattr(
            entry,
            "load_content",
            lambda *args: "Analyze: {user_query}",
        )

        entry.main()

        captured = capsys.readouterr()
        # Should print the complexity assessment prompt
        assert "Analyze: Build an API" in captured.out
        # Should NOT contain routing output
        assert "Last Algorithm" not in captured.out
        assert "DA Direct Execution" not in captured.out
