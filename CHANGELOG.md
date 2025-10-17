# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-17

### Added

- **Audio Support**: Automatically fetches and downloads audio pronunciation files
  - `fetch_audio()` function for downloading audio files from vndic.net
  - Audio URL extraction in `parse_dictionary_content()`
  - Audio field is automatically populated with pronunciation audio
- **Type-Safe Configuration**: Implemented dataclasses for configuration management
  - `FieldMapping` dataclass for field name mappings
  - `Shortcuts` dataclass for keyboard shortcuts
  - `ApiSettings` dataclass for API settings
  - `Config` dataclass for complete configuration
  - Version field in config.json for future migration support

### Changed

- **Configuration Structure**: Simplified configuration with hardcoded API defaults
  - API settings now use `DEFAULT_API_SETTINGS` constant
  - Removed user-configurable API settings from config.json
  - All config classes are now frozen dataclasses for immutability
- **Code Organization**: Improved code structure and maintainability
  - Extracted `fill_pinyin_field()`, `fill_vietnamese_field()`, and `fill_audio_field()` functions
  - Refactored audio download logic into separate function
  - Used constant `FIELD_MAPPING` for field name lookups
  - Enhanced type hints throughout the codebase

### Removed

- Removed `main.py` file (unused)
- Removed user-configurable API settings (source, timeout_seconds, max_retries)

### Development

- Added user confirmation prompt before release
- Expanded test coverage for audio fetching functionality
- Improved type safety across the codebase

## [0.1.3] - 2025-10-13

### Added

- Notification system with tooltip messages
- Test fixtures for dictionary content parsing

### Changed

- UI hooks now automatically fill pinyin and Vietnamese fields
- Removed square brackets from pinyin output

### Fixed

- Removed hardcoded version string from `__init__.py`
- Build script now outputs to `build/` directory

## [0.1.2] - 2025-10-13

### Added

- Dictionary fetcher for vndic.net with BeautifulSoup4 parser
- Content parser for extracting pinyin and Vietnamese definitions
- Build system with dependency vendoring
- Release automation script (`scripts/release.py`)
- Test fixtures with real HTML samples from vndic.net

### Changed

- Adopted newspaper code structure (high-level methods first)

### Development

- Added build commands to justfile for addon packaging

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

[0.2.0]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/autodefine-cn-vn/releases/tag/v0.1.0
