# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-12

### Added

- **Configuration Management**: Implemented `ConfigManager` class for handling Anki addon configuration
  - Field mapping for Chinese, Pinyin, Vietnamese, and Audio fields
  - API settings configuration
  - Keyboard shortcuts configuration
  - Config reload capability
- **UI Hooks**: Added editor integration with Anki's card editor
  - Auto-define button in editor toolbar
  - Field extraction and insertion utilities
  - Hook registration for editor events
- **Utility Functions**: Created `utils.py` module with helper functions
  - `get_field()`: Extract field values from Anki notes
  - `set_field()`: Update field values in Anki notes
  - `unwrap()`: Safe unwrapping of optional values
- **Test Suite**: Comprehensive test coverage (99%) with pytest
  - Unit tests for config manager
  - Unit tests for UI hooks
  - Unit tests for utility functions
  - Test fixtures and mocking setup

### Changed

- Adopted `src/` layout for better package structure
- Moved `config.json` to correct package location
- Added type annotations throughout codebase
- Refactored UI hooks to use utility methods

### Development

- Added `justfile` for common development tasks (lint, format, test, CI)
- Integrated `ruff` for linting and formatting
- Added pytest with coverage reporting
- Created development documentation in `CLAUDE.md`
- Added `.gitignore` for Python and Anki-specific files

## [0.1.0] - 2025-10-12

### Added

- Initial project setup with UV package manager
- Basic Anki addon structure with `manifest.json`
- Project documentation (README.md, LICENSE)
- Development workflow and todo tracking

[0.1.1]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/autodefine-cn-vn/releases/tag/v0.1.0
