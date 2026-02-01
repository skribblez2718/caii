"""
Language-Specific Defaults

Provides default configuration values for each supported language.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LanguageDefaults:
    """
    Default configuration for a programming language.

    Attributes:
        language: Language identifier
        test_command: Command to run tests
        format_command: Command to format code
        lint_command: Command to lint code
        build_command: Command to build project
        run_command: Command to run project
        test_directory: Default test directory
        entry_point: Typical entry point file
        import_style: Import style description
        python_version: Python version (if applicable)
        constraints: Default constraints for the language
        naming_conventions: File naming conventions
    """

    language: str
    test_command: str = "make test"
    format_command: Optional[str] = None
    lint_command: Optional[str] = None
    build_command: Optional[str] = None
    run_command: Optional[str] = None
    test_directory: str = "tests/"
    entry_point: str = "main"
    import_style: str = "absolute"
    python_version: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    naming_conventions: Dict[str, str] = field(default_factory=dict)


# Language defaults registry
LANGUAGE_DEFAULTS: Dict[str, LanguageDefaults] = {
    "python": LanguageDefaults(
        language="python",
        test_command="pytest",
        format_command="black .",
        lint_command="pylint",
        build_command="pip install -e .",
        run_command="python main.py",
        test_directory="tests/",
        entry_point="main.py",
        import_style="absolute",
        python_version="3.11+",
        constraints=[
            "Use absolute imports only (never relative)",
            "Type hints required on all functions",
            "Follow PEP 8 style guidelines",
        ],
        naming_conventions={
            "Modules": "snake_case.py",
            "Classes": "PascalCase",
            "Functions": "snake_case",
            "Constants": "UPPER_SNAKE_CASE",
        },
    ),
    "typescript": LanguageDefaults(
        language="typescript",
        test_command="npm test",
        format_command="npm run format",
        lint_command="npm run lint",
        build_command="npm run build",
        run_command="npm start",
        test_directory="tests/",
        entry_point="src/index.ts",
        import_style="esm",
        constraints=[
            "Use strict TypeScript configuration",
            "Prefer named exports over default exports",
            "Use explicit type annotations",
        ],
        naming_conventions={
            "Files": "kebab-case.ts",
            "Components": "PascalCase.tsx",
            "Utilities": "camelCase.ts",
            "Types": "PascalCase",
        },
    ),
    "javascript": LanguageDefaults(
        language="javascript",
        test_command="npm test",
        format_command="npm run format",
        lint_command="npm run lint",
        build_command="npm run build",
        run_command="npm start",
        test_directory="tests/",
        entry_point="src/index.js",
        import_style="esm",
        constraints=[
            "Use ESM imports/exports",
            "Use JSDoc for documentation",
        ],
        naming_conventions={
            "Files": "kebab-case.js",
            "Functions": "camelCase",
            "Constants": "UPPER_SNAKE_CASE",
        },
    ),
    "rust": LanguageDefaults(
        language="rust",
        test_command="cargo test",
        format_command="cargo fmt",
        lint_command="cargo clippy",
        build_command="cargo build",
        run_command="cargo run",
        test_directory="tests/",
        entry_point="src/main.rs",
        import_style="use statements",
        constraints=[
            "Run clippy before committing",
            "Use derive macros where appropriate",
            "Document public APIs",
        ],
        naming_conventions={
            "Modules": "snake_case.rs",
            "Types": "PascalCase",
            "Functions": "snake_case",
            "Constants": "UPPER_SNAKE_CASE",
        },
    ),
    "go": LanguageDefaults(
        language="go",
        test_command="go test ./...",
        format_command="go fmt ./...",
        lint_command="golangci-lint run",
        build_command="go build",
        run_command="go run .",
        test_directory="",  # Go tests are alongside code
        entry_point="main.go",
        import_style="import",
        constraints=[
            "Run go fmt before committing",
            "Use gofmt/goimports",
            "Handle errors explicitly",
        ],
        naming_conventions={
            "Files": "snake_case.go",
            "Packages": "lowercase",
            "Exported": "PascalCase",
            "Unexported": "camelCase",
        },
    ),
    "java": LanguageDefaults(
        language="java",
        test_command="mvn test",
        format_command="mvn spotless:apply",
        lint_command="mvn checkstyle:check",
        build_command="mvn package",
        run_command="mvn exec:java",
        test_directory="src/test/java/",
        entry_point="src/main/java/Main.java",
        import_style="import",
        constraints=[
            "Follow Java naming conventions",
            "Use Maven/Gradle build system",
        ],
        naming_conventions={
            "Classes": "PascalCase.java",
            "Packages": "lowercase",
            "Methods": "camelCase",
            "Constants": "UPPER_SNAKE_CASE",
        },
    ),
    "unknown": LanguageDefaults(
        language="unknown",
        test_command="make test",
        test_directory="tests/",
        entry_point="main",
        constraints=[
            "Document build and run commands",
        ],
        naming_conventions={},
    ),
}


def get_language_defaults(language: str) -> LanguageDefaults:
    """
    Get default configuration for a language.

    Args:
        language: Language identifier

    Returns:
        LanguageDefaults for the language, or defaults for 'unknown'

    Example:
        defaults = get_language_defaults("python")
        print(defaults.test_command)  # "pytest"
    """
    return LANGUAGE_DEFAULTS.get(language, LANGUAGE_DEFAULTS["unknown"])


def get_supported_languages() -> List[str]:
    """
    Get list of supported languages.

    Returns:
        List of language identifiers
    """
    return [lang for lang in LANGUAGE_DEFAULTS if lang != "unknown"]
