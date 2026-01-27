"""
Unit tests for utils.py

Tests utility functions: get_content_dir, load_content, substitute_placeholders.
"""

import pytest
from pathlib import Path

# ============================================================================
# TestGetContentDir
# ============================================================================


class TestGetContentDir:
    """Tests for get_content_dir() function."""

    @pytest.mark.unit
    def test_returns_path_object(self, tmp_path):
        """Should return a Path object."""
        from orchestration.utils import get_content_dir

        script_path = tmp_path / "script.py"
        script_path.touch()

        result = get_content_dir(str(script_path))

        assert isinstance(result, Path)

    @pytest.mark.unit
    def test_content_dir_is_sibling_to_script(self, tmp_path):
        """Content dir should be sibling 'content' directory to script."""
        from orchestration.utils import get_content_dir

        script_path = tmp_path / "myscript.py"

        result = get_content_dir(str(script_path))

        assert result == tmp_path / "content"

    @pytest.mark.unit
    def test_works_with_nested_path(self, tmp_path):
        """Should work with deeply nested script paths."""
        from orchestration.utils import get_content_dir

        script_path = tmp_path / "outer_loop" / "gather" / "entry.py"
        script_path.parent.mkdir(parents=True)
        script_path.touch()

        result = get_content_dir(str(script_path))

        assert result == tmp_path / "outer_loop" / "gather" / "content"


# ============================================================================
# TestLoadContent
# ============================================================================


class TestLoadContent:
    """Tests for load_content() function."""

    @pytest.mark.unit
    def test_returns_file_contents(self, tmp_path):
        """Should return contents of the specified file."""
        from orchestration.utils import load_content

        # Create content directory and file
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        content_file = content_dir / "test.md"
        content_file.write_text("# Test Content\n\nHello, world!")

        script_path = tmp_path / "script.py"
        script_path.touch()

        result = load_content(str(script_path), "test.md")

        assert result == "# Test Content\n\nHello, world!"

    @pytest.mark.unit
    def test_returns_empty_for_missing_file(self, tmp_path):
        """Should return empty string if file doesn't exist."""
        from orchestration.utils import load_content

        # Create content directory but no file
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        script_path = tmp_path / "script.py"
        script_path.touch()

        result = load_content(str(script_path), "nonexistent.md")

        assert result == ""

    @pytest.mark.unit
    def test_returns_empty_for_missing_content_dir(self, tmp_path):
        """Should return empty string if content directory doesn't exist."""
        from orchestration.utils import load_content

        script_path = tmp_path / "script.py"
        script_path.touch()

        result = load_content(str(script_path), "test.md")

        assert result == ""

    @pytest.mark.unit
    def test_loads_with_md_extension(self, tmp_path):
        """Should correctly load .md files."""
        from orchestration.utils import load_content

        content_dir = tmp_path / "content"
        content_dir.mkdir()
        (content_dir / "phase.md").write_text("Phase content here")

        script_path = tmp_path / "script.py"

        result = load_content(str(script_path), "phase.md")

        assert result == "Phase content here"


# ============================================================================
# TestSubstitutePlaceholders
# ============================================================================


class TestSubstitutePlaceholders:
    """Tests for substitute_placeholders() function."""

    @pytest.mark.unit
    def test_substitutes_single_placeholder(self):
        """Should substitute a single placeholder."""
        from orchestration.utils import substitute_placeholders

        content = "Hello, {name}!"

        result = substitute_placeholders(content, name="World")

        assert result == "Hello, World!"

    @pytest.mark.unit
    def test_substitutes_multiple_placeholders(self):
        """Should substitute multiple different placeholders."""
        from orchestration.utils import substitute_placeholders

        content = "User: {user}, Query: {query}"

        result = substitute_placeholders(content, user="Alice", query="Build API")

        assert result == "User: Alice, Query: Build API"

    @pytest.mark.unit
    def test_substitutes_repeated_placeholder(self):
        """Should substitute the same placeholder multiple times."""
        from orchestration.utils import substitute_placeholders

        content = "{name} says hello. Hello from {name}!"

        result = substitute_placeholders(content, name="Bob")

        assert result == "Bob says hello. Hello from Bob!"

    @pytest.mark.unit
    def test_converts_to_string(self):
        """Should convert non-string values to string."""
        from orchestration.utils import substitute_placeholders

        content = "Count: {count}, Value: {value}"

        result = substitute_placeholders(content, count=42, value=3.14)

        assert result == "Count: 42, Value: 3.14"

    @pytest.mark.unit
    def test_preserves_unmatched_placeholders(self):
        """Should preserve placeholders that don't have a replacement."""
        from orchestration.utils import substitute_placeholders

        content = "Name: {name}, Unknown: {other}"

        result = substitute_placeholders(content, name="Test")

        assert result == "Name: Test, Unknown: {other}"

    @pytest.mark.unit
    def test_empty_content_returns_empty(self):
        """Should return empty string for empty content."""
        from orchestration.utils import substitute_placeholders

        result = substitute_placeholders("", name="Test")

        assert result == ""

    @pytest.mark.unit
    def test_no_placeholders_returns_unchanged(self):
        """Should return unchanged content if no placeholders."""
        from orchestration.utils import substitute_placeholders

        content = "No placeholders here."

        result = substitute_placeholders(content, name="Test")

        assert result == "No placeholders here."

    @pytest.mark.unit
    def test_no_kwargs_returns_unchanged(self):
        """Should return unchanged content if no kwargs provided."""
        from orchestration.utils import substitute_placeholders

        content = "Hello, {name}!"

        result = substitute_placeholders(content)

        assert result == "Hello, {name}!"

    @pytest.mark.unit
    def test_multiline_content(self):
        """Should handle multiline content."""
        from orchestration.utils import substitute_placeholders

        content = """# Title: {title}

Section for {user}.

End of document."""

        result = substitute_placeholders(content, title="Test Doc", user="Alice")

        expected = """# Title: Test Doc

Section for Alice.

End of document."""
        assert result == expected

    @pytest.mark.unit
    def test_complex_real_world_example(self):
        """Should handle real-world content with session_id and user_query."""
        from orchestration.utils import substitute_placeholders

        content = """# Phase: GATHER
Session: {session_id}

## User Query
{user_query}

## Instructions
Analyze the query for session {session_id}."""

        result = substitute_placeholders(
            content,
            session_id="abc123def456",
            user_query="Build a REST API",
        )

        assert "Session: abc123def456" in result
        assert "Build a REST API" in result
        assert result.count("abc123def456") == 2
