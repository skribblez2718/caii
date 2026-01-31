"""
Language Detector Unit Tests

Tests for language and framework detection.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestLanguageDetection:
    """Tests for detect_language function."""

    def test_detect_python_from_pyproject(self, tmp_path: Path):
        """Should detect Python from pyproject.toml."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = 'test'")

        info = detect_language(tmp_path)

        assert info.language == "python"
        assert info.manifest_file == "pyproject.toml"

    def test_detect_python_from_requirements(self, tmp_path: Path):
        """Should detect Python from requirements.txt."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "requirements.txt").write_text("flask>=2.0")

        info = detect_language(tmp_path)

        assert info.language == "python"
        assert info.manifest_file == "requirements.txt"

    def test_detect_typescript_from_tsconfig(self, tmp_path: Path):
        """Should detect TypeScript from tsconfig.json with package.json."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

        info = detect_language(tmp_path)

        assert info.language == "typescript"
        assert info.package_manager == "npm"

    def test_detect_javascript_from_package_json(self, tmp_path: Path):
        """Should detect JavaScript from package.json alone."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "package.json").write_text('{"name": "test"}')

        info = detect_language(tmp_path)

        assert info.language == "javascript"
        assert info.manifest_file == "package.json"

    def test_detect_rust_from_cargo(self, tmp_path: Path):
        """Should detect Rust from Cargo.toml."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"')

        info = detect_language(tmp_path)

        assert info.language == "rust"
        assert info.package_manager == "cargo"

    def test_detect_go_from_go_mod(self, tmp_path: Path):
        """Should detect Go from go.mod."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "go.mod").write_text("module test")

        info = detect_language(tmp_path)

        assert info.language == "go"
        assert info.package_manager == "go"

    def test_detect_java_maven(self, tmp_path: Path):
        """Should detect Java from pom.xml."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "pom.xml").write_text("<project></project>")

        info = detect_language(tmp_path)

        assert info.language == "java"
        assert info.framework == "maven"

    def test_detect_java_gradle(self, tmp_path: Path):
        """Should detect Java from build.gradle."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        (tmp_path / "build.gradle").write_text("plugins { id 'java' }")

        info = detect_language(tmp_path)

        assert info.language == "java"
        assert info.framework == "gradle"

    def test_detect_unknown_for_empty_directory(self, tmp_path: Path):
        """Should return unknown for empty directory."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        info = detect_language(tmp_path)

        assert info.language == "unknown"

    def test_detect_unknown_for_nonexistent_path(self, tmp_path: Path):
        """Should return unknown for nonexistent path."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        info = detect_language(tmp_path / "nonexistent")

        assert info.language == "unknown"

    def test_fallback_to_extension_detection(self, tmp_path: Path):
        """Should fallback to extension detection when no manifest."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        # Create Python files without manifest
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")

        info = detect_language(tmp_path)

        assert info.language == "python"

    def test_priority_python_over_extension(self, tmp_path: Path):
        """Manifest detection should take priority over extension detection."""
        from orchestration.skills.scaffold_docs.detector import detect_language

        # Create both Python manifest and Go files
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]")
        (tmp_path / "main.go").write_text("package main")

        info = detect_language(tmp_path)

        # pyproject.toml should win
        assert info.language == "python"


@pytest.mark.unit
class TestFrameworkDetection:
    """Tests for framework detection."""

    def test_detect_django(self, tmp_path: Path):
        """Should detect Django framework."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks

        (tmp_path / "requirements.txt").write_text("Django>=4.0")

        frameworks = detect_frameworks(tmp_path, "python")

        assert "django" in frameworks

    def test_detect_flask(self, tmp_path: Path):
        """Should detect Flask framework."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks

        (tmp_path / "requirements.txt").write_text("flask>=2.0")

        frameworks = detect_frameworks(tmp_path, "python")

        assert "flask" in frameworks

    def test_detect_fastapi(self, tmp_path: Path):
        """Should detect FastAPI framework."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks

        (tmp_path / "pyproject.toml").write_text(
            '[project]\ndependencies = ["fastapi"]'
        )

        frameworks = detect_frameworks(tmp_path, "python")

        assert "fastapi" in frameworks

    def test_detect_react(self, tmp_path: Path):
        """Should detect React framework."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks
        import json

        pkg = {"dependencies": {"react": "^18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))

        frameworks = detect_frameworks(tmp_path, "javascript")

        assert "react" in frameworks

    def test_detect_express(self, tmp_path: Path):
        """Should detect Express framework."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks
        import json

        pkg = {"dependencies": {"express": "^4.18.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))

        frameworks = detect_frameworks(tmp_path, "javascript")

        assert "express" in frameworks

    def test_no_frameworks_detected(self, tmp_path: Path):
        """Should return empty list when no frameworks detected."""
        from orchestration.skills.scaffold_docs.detector import detect_frameworks

        frameworks = detect_frameworks(tmp_path, "python")

        assert frameworks == []


@pytest.mark.unit
class TestLanguageInfo:
    """Tests for LanguageInfo dataclass."""

    def test_language_info_creation(self):
        """LanguageInfo should be created with all fields."""
        from orchestration.skills.scaffold_docs.detector import LanguageInfo

        info = LanguageInfo(
            language="python",
            framework="django",
            version="3.11",
            package_manager="pip",
            manifest_file="pyproject.toml",
        )

        assert info.language == "python"
        assert info.framework == "django"
        assert info.version == "3.11"
        assert info.package_manager == "pip"
        assert info.manifest_file == "pyproject.toml"

    def test_language_info_defaults(self):
        """LanguageInfo should have sensible defaults."""
        from orchestration.skills.scaffold_docs.detector import LanguageInfo

        info = LanguageInfo(language="unknown")

        assert info.framework is None
        assert info.version is None
        assert info.package_manager is None
        assert info.manifest_file is None
