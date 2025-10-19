# AutoDefine Chinese-Vietnamese Anki Addon - Justfile

# List all available commands
default:
    @just --list

# ============================================================================
# Setup & Dependencies
# ============================================================================

# Install dependencies including dev extras
install:
    uv sync --extra dev

# ============================================================================
# Code Quality
# ============================================================================

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

# Run linter and formatter together
check: lint format-check

# Fix all issues (lint + format)
fix: lint-fix format

# Run full CI pipeline (format, lint, test)
ci: format lint test

# ============================================================================
# Testing
# ============================================================================

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

# ============================================================================
# Development Workflow
# ============================================================================

# Link addon to Anki's addon folder for development (macOS)
link-to-anki: build
    uv run python scripts/link_to_anki.py

# Build and run Anki with Test profile for manual testing (macOS)
run-anki-macos: build
    /Applications/Anki.app/Contents/MacOS/launcher -p Test

# ============================================================================
# Build & Release
# ============================================================================

# Build Anki addon package
build: clean-build
    uv run python scripts/build.py

# Get current version from pyproject.toml
version:
    @uv run python scripts/release.py --help | grep "Current version" || grep '^version = ' pyproject.toml | sed 's/version = \"\\(.*\\)\"/\\1/'

# Release a new version (e.g., just release 0.1.2)
release VERSION:
    uv run python scripts/release.py {{VERSION}}

# Release a patch version (e.g., 0.1.0 -> 0.1.1)
release-patch:
    uv run python scripts/release.py --patch

# Release a minor version (e.g., 0.1.0 -> 0.2.0)
release-minor:
    uv run python scripts/release.py --minor

# Release a major version (e.g., 0.1.0 -> 1.0.0)
release-major:
    uv run python scripts/release.py --major

# Dry run release to see what would happen
release-dry-run VERSION:
    uv run python scripts/release.py {{VERSION}} --dry-run

# Dry run patch release
release-patch-dry:
    uv run python scripts/release.py --patch --dry-run

# ============================================================================
# Cleanup
# ============================================================================

# Clean up generated files
clean:
    rm -rf .pytest_cache .ruff_cache htmlcov .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Clean build artifacts
clean-build:
    rm -rf dist/ build/
