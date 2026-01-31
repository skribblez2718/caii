"""
Language and Framework Detection

Detects project language and framework based on manifest files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class LanguageInfo:
    """
    Detected language information.

    Attributes:
        language: Primary language identifier
        framework: Detected framework (if any)
        version: Language/runtime version (if detectable)
        package_manager: Package manager used
        manifest_file: The file that determined detection
    """

    language: str
    framework: Optional[str] = None
    version: Optional[str] = None
    package_manager: Optional[str] = None
    manifest_file: Optional[str] = None


# Detection rules: (manifest_file, language, framework, package_manager)
DETECTION_RULES: List[tuple] = [
    # Python
    ("pyproject.toml", "python", None, "pip/poetry"),
    ("setup.py", "python", None, "pip"),
    ("requirements.txt", "python", None, "pip"),
    ("Pipfile", "python", None, "pipenv"),
    # Node.js / TypeScript
    ("package.json", "javascript", None, "npm"),  # TypeScript detected separately
    ("tsconfig.json", "typescript", None, "npm"),
    ("pnpm-lock.yaml", "javascript", None, "pnpm"),
    ("yarn.lock", "javascript", None, "yarn"),
    # Rust
    ("Cargo.toml", "rust", None, "cargo"),
    # Go
    ("go.mod", "go", None, "go"),
    # Java/Kotlin
    ("pom.xml", "java", "maven", "maven"),
    ("build.gradle", "java", "gradle", "gradle"),
    ("build.gradle.kts", "kotlin", "gradle", "gradle"),
    # Ruby
    ("Gemfile", "ruby", None, "bundler"),
    # PHP
    ("composer.json", "php", None, "composer"),
    # C#/.NET
    ("*.csproj", "csharp", "dotnet", "nuget"),
    ("*.fsproj", "fsharp", "dotnet", "nuget"),
    # Elixir
    ("mix.exs", "elixir", None, "mix"),
    # Scala
    ("build.sbt", "scala", "sbt", "sbt"),
    # Swift
    ("Package.swift", "swift", None, "spm"),
]


def detect_language(project_path: Path) -> LanguageInfo:
    """
    Detect project language based on manifest files.

    Args:
        project_path: Path to project root directory

    Returns:
        LanguageInfo with detected language information

    Example:
        info = detect_language(Path("/home/user/my-project"))
        print(info.language)  # "python"
    """
    if not project_path.exists() or not project_path.is_dir():
        return LanguageInfo(language="unknown")

    # Track TypeScript detection for JS projects
    has_tsconfig = (project_path / "tsconfig.json").exists()

    for rule in DETECTION_RULES:
        manifest_pattern, language, framework, package_manager = rule

        # Handle glob patterns
        if "*" in manifest_pattern:
            matches = list(project_path.glob(manifest_pattern))
            if matches:
                manifest_file = matches[0].name
                return LanguageInfo(
                    language=language,
                    framework=framework,
                    package_manager=package_manager,
                    manifest_file=manifest_file,
                )
        else:
            manifest_path = project_path / manifest_pattern
            if manifest_path.exists():
                # Special case: JavaScript with TypeScript
                if manifest_pattern == "package.json" and has_tsconfig:
                    return LanguageInfo(
                        language="typescript",
                        framework=framework,
                        package_manager=package_manager,
                        manifest_file=manifest_pattern,
                    )

                return LanguageInfo(
                    language=language,
                    framework=framework,
                    package_manager=package_manager,
                    manifest_file=manifest_pattern,
                )

    # No manifest found - try to detect from file extensions
    return _detect_from_extensions(project_path)


def _detect_from_extensions(project_path: Path) -> LanguageInfo:
    """
    Fallback detection based on file extensions.

    Args:
        project_path: Path to project root directory

    Returns:
        LanguageInfo based on most common file extensions
    """
    extension_counts: dict = {}

    # Extension to language mapping
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".ex": "elixir",
        ".exs": "elixir",
        ".scala": "scala",
        ".swift": "swift",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

    # Count files by language
    for ext, lang in extension_map.items():
        count = len(list(project_path.rglob(f"*{ext}")))
        if count > 0:
            extension_counts[lang] = extension_counts.get(lang, 0) + count

    if not extension_counts:
        return LanguageInfo(language="unknown")

    # Return most common language
    most_common = max(extension_counts, key=lambda k: extension_counts[k])
    return LanguageInfo(language=most_common)


def detect_frameworks(project_path: Path, language: str) -> List[str]:
    """
    Detect frameworks for a given language.

    Args:
        project_path: Path to project root directory
        language: Detected language

    Returns:
        List of detected framework names
    """
    frameworks: List[str] = []

    if language == "python":
        # Check common Python frameworks
        requirements_files = [
            project_path / "requirements.txt",
            project_path / "pyproject.toml",
            project_path / "setup.py",
        ]

        framework_indicators = {
            "django": ["django"],
            "flask": ["flask"],
            "fastapi": ["fastapi"],
            "pytest": ["pytest"],
            "click": ["click"],
        }

        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text().lower()
                for framework, indicators in framework_indicators.items():
                    if any(ind in content for ind in indicators):
                        frameworks.append(framework)

    elif language in ("javascript", "typescript"):
        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            import json

            try:
                pkg = json.loads(package_json.read_text())
                deps = {
                    **pkg.get("dependencies", {}),
                    **pkg.get("devDependencies", {}),
                }

                framework_map = {
                    "react": "react",
                    "vue": "vue",
                    "angular": "@angular/core",
                    "next": "next",
                    "express": "express",
                    "nestjs": "@nestjs/core",
                }

                for framework, dep in framework_map.items():
                    if dep in deps:
                        frameworks.append(framework)
            except json.JSONDecodeError:
                pass

    return frameworks
