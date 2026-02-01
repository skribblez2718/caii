"""
Language Defaults Unit Tests

Tests for language-specific default configurations.
"""

import pytest


@pytest.mark.unit
class TestLanguageDefaults:
    """Tests for language defaults."""

    def test_get_python_defaults(self):
        """Should return Python defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("python")

        assert defaults.language == "python"
        assert defaults.test_command == "pytest"
        assert "absolute" in defaults.import_style.lower()
        assert defaults.python_version is not None

    def test_get_typescript_defaults(self):
        """Should return TypeScript defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("typescript")

        assert defaults.language == "typescript"
        assert "npm" in defaults.test_command
        assert defaults.entry_point.endswith(".ts")

    def test_get_javascript_defaults(self):
        """Should return JavaScript defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("javascript")

        assert defaults.language == "javascript"
        assert "npm" in defaults.test_command
        assert defaults.entry_point.endswith(".js")

    def test_get_rust_defaults(self):
        """Should return Rust defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("rust")

        assert defaults.language == "rust"
        assert "cargo" in defaults.test_command
        assert defaults.lint_command == "cargo clippy"

    def test_get_go_defaults(self):
        """Should return Go defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("go")

        assert defaults.language == "go"
        assert "go test" in defaults.test_command
        assert defaults.format_command == "go fmt ./..."

    def test_get_java_defaults(self):
        """Should return Java defaults."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("java")

        assert defaults.language == "java"
        assert "mvn" in defaults.test_command
        assert defaults.test_directory == "src/test/java/"

    def test_get_unknown_defaults(self):
        """Should return unknown defaults for unsupported language."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("unknown")

        assert defaults.language == "unknown"
        assert defaults.test_command == "make test"

    def test_unsupported_language_returns_unknown(self):
        """Should return unknown defaults for unsupported language."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("brainfuck")

        assert defaults.language == "unknown"

    def test_python_constraints(self):
        """Python defaults should include key constraints."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("python")

        constraints_text = " ".join(defaults.constraints).lower()
        assert "absolute" in constraints_text
        assert "type" in constraints_text or "hint" in constraints_text

    def test_naming_conventions_exist(self):
        """Language defaults should include naming conventions."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_language_defaults,
        )

        defaults = get_language_defaults("python")

        assert len(defaults.naming_conventions) > 0
        assert (
            "Modules" in defaults.naming_conventions
            or "Files" in defaults.naming_conventions
        )

    def test_get_supported_languages(self):
        """Should return list of supported languages."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            get_supported_languages,
        )

        languages = get_supported_languages()

        assert "python" in languages
        assert "typescript" in languages
        assert "javascript" in languages
        assert "rust" in languages
        assert "go" in languages
        assert "java" in languages
        assert "unknown" not in languages


@pytest.mark.unit
class TestLanguageDefaultsDataclass:
    """Tests for LanguageDefaults dataclass."""

    def test_dataclass_fields(self):
        """LanguageDefaults should have all expected fields."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            LanguageDefaults,
        )

        defaults = LanguageDefaults(
            language="test",
            test_command="test cmd",
            format_command="fmt cmd",
            lint_command="lint cmd",
            build_command="build cmd",
            run_command="run cmd",
            test_directory="tests/",
            entry_point="main.test",
            import_style="absolute",
            python_version="3.11",
            constraints=["constraint1"],
            naming_conventions={"Files": "test.py"},
        )

        assert defaults.language == "test"
        assert defaults.test_command == "test cmd"
        assert defaults.format_command == "fmt cmd"
        assert defaults.lint_command == "lint cmd"
        assert defaults.build_command == "build cmd"
        assert defaults.run_command == "run cmd"
        assert defaults.test_directory == "tests/"
        assert defaults.entry_point == "main.test"
        assert defaults.import_style == "absolute"
        assert defaults.python_version == "3.11"
        assert defaults.constraints == ["constraint1"]
        assert defaults.naming_conventions == {"Files": "test.py"}

    def test_dataclass_defaults(self):
        """LanguageDefaults should have sensible default values."""
        from orchestration.skills.scaffold_docs.language_defaults import (
            LanguageDefaults,
        )

        defaults = LanguageDefaults(language="minimal")

        assert defaults.test_command == "make test"
        assert defaults.format_command is None
        assert defaults.test_directory == "tests/"
        assert defaults.constraints == []
        assert defaults.naming_conventions == {}
