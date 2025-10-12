# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki addon that automatically populates Chinese vocabulary cards with Vietnamese translations, pinyin, definitions, and audio pronunciations. The addon integrates with Anki's card editor through hooks and provides keyboard shortcuts (Ctrl+Alt+D) for manual triggering.

## Development Commands

This project uses `uv` for dependency management and `just` for task running.

### Setup

```bash
uv sync --extra dev
```

### Common Commands (via justfile)

```bash
just lint          # Run ruff linter
just lint-fix      # Auto-fix linting issues
just format        # Format code with ruff
just format-check  # Check formatting without changes
just test          # Run pytest tests
just test-cov      # Run tests with coverage report
just check         # Run lint + format check
just fix           # Auto-fix lint + format issues
just ci            # Run full CI pipeline (format, lint, test)
just clean         # Remove generated files and caches
```

### Running Individual Tests

```bash
uv run pytest tests/test_specific.py
uv run pytest tests/test_specific.py::test_function_name
```

## Architecture

### Anki Addon Package Structure

Anki addons must follow a specific structure:

- Anki addon development doc is at https://addon-docs.ankiweb.net/intro.html
- The addon code lives in `src/autodefine_cn_vn/` during development
- The `__init__.py` is the entry point that Anki loads when the addon is activated
- `config.json` defines default configuration (field mappings, API settings, shortcuts)
- For distribution, the entire `autodefine_cn_vn/` folder is packaged into an `.ankiaddon` file (which is a renamed .zip file)
- When installed, Anki extracts the addon to its `addons21/` directory
- You can use ../autodefine_oxfordlearnersdictionaries as reference

### Anki Addon Structure

The main entry point (`__init__.py`) registers hooks with Anki's event system:

- **profileLoaded hook**: Initializes the addon when an Anki profile loads
- **Menu integration**: Adds settings to Anki's Tools menu
- **Field mapping**: Maps addon outputs to configurable Anki card fields

### Configuration

Default configuration is in `config.json`:

- Field mapping: Defines which Anki fields receive which data (Chinese, Pinyin, Vietnamese, Audio)
- API settings: Translation source URL template and network settings
- Shortcuts: Keyboard shortcuts for triggering auto-definition

## Key Technical Considerations

- **Anki API compatibility**: This addon targets Anki 24.0.0+ (uses aqt, anki modules)
- **Python version**: Requires Python 3.12+
- **Async operations**: Network requests to translation APIs should handle timeouts and retries
- **Field detection**: Must handle various note types and custom field names through configuration
- **Error handling**: Network failures and parsing errors should fail gracefully without breaking Anki

## Translation Data Source

The addon fetches Vietnamese translations from: `http://2.vndic.net/index.php?word={}&dict=cn_vi`

This requires web scraping or API integration to extract translation data.

## Reference Implementation

This addon is inspired by [AutoDefine Oxford Learners Dictionaries](https://github.com/artyompetrov/AutoDefine_oxfordlearnersdictionaries), which provides a similar auto-definition workflow for English vocabulary.
