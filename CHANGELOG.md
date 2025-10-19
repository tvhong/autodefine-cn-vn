# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-10-18

### Added

- **Sample Sentence Support**: Automatically extracts and displays example sentences from vndic.net
  - Automatic highlighting of target Chinese word in bold (`<b>` tags)
  - Sample sentences include both Chinese text and Vietnamese translation

### Development

- Updated CLAUDE.md with comprehensive documentation on sample sentence feature
- Added detailed HTML structure examples for vndic.net parsing
- Expanded test coverage for sample sentence extraction
- **Build System Improvements**:
  - Build script now displays output path after successful build
  - Gitignored files are no longer copied during build process
  - Automatic cleanup now runs before each build
  - Added `run-anki-macos` command to justfile for easier testing on macOS
- **Code Quality**:
  - Added `DictionaryContent` TypedDict for type-safe dictionary parsing results
  - Improved code organization with consistent top-level imports
  - Separated highlighting logic from parsing (now done during field insertion)
  - Enhanced type hints with `dict` type annotations in UI hooks

## [0.2.0] - 2025-10-17

### Added

- **Audio Support**: Automatically fetches and downloads audio pronunciation files
- **Type-Safe Configuration**: Implemented dataclasses for configuration management

### Changed

- **Configuration Structure**: Simplified configuration with hardcoded API defaults
- **Code Organization**: Improved code structure and maintainability

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
- **UI Hooks**: Added editor integration with Anki's card editor
- **Utility Functions**: Created `utils.py` module with helper functions
- **Test Suite**: Comprehensive test coverage (99%) with pytest

### Development

- Added type annotations throughout codebase
- Refactored UI hooks to use utility methods
- Moved `config.json` to correct package location
- Adopted `src/` layout for better package structure
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

[0.2.1]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/yourusername/autodefine-cn-vn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/autodefine-cn-vn/releases/tag/v0.1.0
