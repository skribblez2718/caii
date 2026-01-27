# CAII Orchestration Development Makefile
# ========================================
#
# Usage:
#   make test          - Run all tests
#   make test-unit     - Run unit tests only
#   make test-int      - Run integration tests only
#   make coverage      - Run tests with coverage report
#   make format        - Format code with black
#   make lint          - Run pylint
#   make typecheck     - Run mypy type checking
#   make all           - Format, lint, typecheck, and test

.PHONY: test test-unit test-int test-e2e coverage format lint typecheck all clean help

# Default target
help:
	@echo "CAII Orchestration Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests"
	@echo "  make test-unit     Run unit tests only"
	@echo "  make test-int      Run integration tests only"
	@echo "  make test-e2e      Run end-to-end tests only"
	@echo "  make coverage      Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        Format code with black"
	@echo "  make lint          Run pylint"
	@echo "  make typecheck     Run mypy type checking"
	@echo ""
	@echo "Combined:"
	@echo "  make all           Format, lint, typecheck, and test"
	@echo "  make clean         Remove build artifacts"

# Testing targets
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit -v -m unit

test-int:
	pytest tests/integration -v -m integration

test-e2e:
	pytest tests/e2e -v -m e2e

coverage:
	pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-config=pyproject.toml

# Code quality targets
format:
	black . --exclude="\.venv"

lint:
	pylint . --ignore=.venv,tests --rcfile=pyproject.toml

typecheck:
	mypy . --exclude=".venv" --config-file=pyproject.toml

# Combined target
all: format lint typecheck test

# Cleanup
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
