# AutoDefine Chinese-Vietnamese Anki Addon - Justfile

# List all available commands
default:
    @just --list

# Install dependencies including dev extras
install:
    uv sync --extra dev

# Run linter (ruff check)
lint:
    uv run ruff check .

# Fix linting issues automatically
lint-fix:
    uv run ruff check --fix .

# Check code formatting
format-check:
    uv run ruff format --check .

# Format code
format:
    uv run ruff format .

# Run all tests
test:
    uv run pytest

# Run tests with coverage report
test-cov:
    uv run pytest --cov=. --cov-report=term-missing --cov-report=html

# Run tests in verbose mode
test-verbose:
    uv run pytest -vv

# Run specific test file
test-file FILE:
    uv run pytest {{FILE}}

# Run linter and formatter together
check: lint format-check

# Fix all issues (lint + format)
fix: lint-fix format

# Run full CI pipeline (format, lint, test)
ci: format lint test

# Clean up generated files
clean:
    rm -rf .pytest_cache .ruff_cache htmlcov .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build Anki addon package
build:
    @echo "Building Anki addon package..."
    @echo "TODO: Implement build script"

# Run Anki with the addon for testing
run-anki:
    @echo "Starting Anki for manual testing..."
    @echo "TODO: Implement Anki launch script"
