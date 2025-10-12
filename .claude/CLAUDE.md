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

### Anki Addon Structure

Anki addons use a specific structure where the addon code lives in `src/autodefine_cn_vn/`. The main entry point (`__init__.py`) registers hooks with Anki's event system:

- **profileLoaded hook**: Initializes the addon when an Anki profile loads
- **Menu integration**: Adds settings to Anki's Tools menu
- **Field mapping**: Maps addon outputs to configurable Anki card fields

### Planned Module Architecture

The addon will be organized into these core modules:

- **config_manager.py**: Manages user configuration (field mappings, API settings, shortcuts)
- **translator.py**: Orchestrates the translation workflow (Chinese → Vietnamese)
- **text_processor.py**: Handles Chinese text processing (segmentation, character handling)
- **chinese_dict.py**: Fetches Chinese definitions and explanations
- **vietnamese_dict.py**: Fetches Vietnamese translations from vndic.net
- **field_manager.py**: Populates Anki card fields with translation results
- **ui_hooks.py**: Integrates with Anki's card editor UI
- **audio_service.py**: Downloads and embeds pronunciation audio

### Configuration

Default configuration is in `config.json`:
- Field mapping: Defines which Anki fields receive which data (Chinese, Pinyin, Vietnamese, Audio)
- API settings: Translation source URL template and network settings
- Shortcuts: Keyboard shortcuts for triggering auto-definition

## Manual Testing with Anki

To test the addon in Anki:

1. Find Anki's addon directory: Open Anki → Tools → Add-ons → View Files
2. Create a symlink from Anki's addon directory to your local `src/autodefine_cn_vn` directory:
   ```bash
   # Mac example
   ln -s /Users/vy/workplace/autodefine-cn-vn/src/autodefine_cn_vn \
         ~/Library/Application\ Support/Anki2/addons21/autodefine_cn_vn
   ```
3. Create a Test profile in Anki (for safety)
4. Run Anki from terminal to see debug output:
   ```bash
   # Mac
   /Applications/Anki.app/Contents/MacOS/anki -p Test

   # Linux
   /usr/local/bin/anki -p Test
   ```
5. Make code changes, restart Anki, and test

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
