# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki addon (v0.1.2) that automatically populates Chinese vocabulary cards with Vietnamese translations and pinyin pronunciations. The addon integrates with Anki's card editor through hooks and provides an editor button with keyboard shortcut (Ctrl+Alt+D) for manual triggering.

**Key Features:**

- Fetches translations from http://2.vndic.net/index.php?word={}&dict=cn_vi
- Parses pinyin pronunciation and Vietnamese definitions using BeautifulSoup4
- Configurable field mapping for different note types
- Editor toolbar button with customizable keyboard shortcuts
- Notification system with tooltips
- Comprehensive error handling for network failures

## Development Commands

This project uses `uv` for dependency management and `just` for task running.

### Setup

```bash
# Install dependencies including dev extras
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
just test-verbose  # Run tests in verbose mode
just check         # Run lint + format check
just fix           # Auto-fix lint + format issues
just ci            # Run full CI pipeline (format, lint, test)
just clean         # Remove generated files and caches
just clean-build   # Remove build artifacts

# Build and release commands
just build              # Build Anki addon package (.ankiaddon file)
just version            # Show current version
just release VERSION    # Release a new version (e.g., just release 0.1.3)
just release-patch      # Release a patch version (0.1.2 -> 0.1.3)
just release-minor      # Release a minor version (0.1.2 -> 0.2.0)
just release-major      # Release a major version (0.1.2 -> 1.0.0)
just release-dry-run VERSION  # Dry run to preview release changes
```

### Running Individual Tests

```bash
uv run pytest tests/test_specific.py
uv run pytest tests/test_specific.py::test_function_name

# Or using just
just test-file tests/test_specific.py
```

## Architecture

### Project Structure

```
src/autodefine_cn_vn/
├── __init__.py           # Entry point: hooks registration and menu setup
├── config.json           # Default configuration
├── config_manager.py     # ConfigManager class for reading Anki addon config
├── fetcher.py            # Web scraping: format_url, fetch_webpage, parse_dictionary_content
├── ui_hooks.py           # Editor integration: setup_editor_buttons, auto_define
├── utils.py              # Utility functions: notify, get_field, set_field, unwrap
└── vendor/               # Bundled dependencies (bs4, soupsieve, typing-extensions)
```

### Core Modules

**`__init__.py`** - Entry point that Anki loads when the addon is activated

- Registers `profileLoaded` hook to initialize the addon
- Sets up "AutoDefine CN-VN Settings" menu in Tools menu
- Adds vendor directory to sys.path for bundled dependencies

**`config_manager.py`** - Configuration management using Anki's config API

- `ConfigManager` class with methods: `get_field_mapping()`, `get_shortcuts()`, `get_api_settings()`
- Loads configuration from Anki's addon manager
- Supports config reloading

**`fetcher.py`** - Web scraping and parsing

- `format_url(url_template, chinese_word)`: Formats URL with Chinese word
- `fetch_webpage(url, timeout)`: Fetches HTML content from vndic.net
- `parse_dictionary_content(html_content)`: Extracts pinyin and Vietnamese definitions using BeautifulSoup4

**`ui_hooks.py`** - Anki editor integration

- `init_ui_hooks()`: Registers editor button setup hook
- `setup_editor_buttons(buttons, editor)`: Adds "自動" button to editor toolbar
- `auto_define(editor)`: Main logic to fetch and populate fields
- `get_chinese_text(editor)`: Extracts Chinese text from configured field
- `insert_into_field(editor, text, field_name, overwrite)`: Updates note fields

**`utils.py`** - Anki note utilities

- `notify(message, period)`: Shows tooltip and prints to stdout
- `get_field(note, field_name)`: Gets field value by name
- `set_field(note, field, value)`: Sets field value by name
- `unwrap(obj)`: Unwraps optional values safely

### Anki Addon Package Structure

- Anki addon development docs: https://addon-docs.ankiweb.net/intro.html
- Development: Code lives in `src/autodefine_cn_vn/`
- Distribution: Packaged into `.ankiaddon` file (renamed .zip) by `scripts/build.py`
- Installation: Anki extracts to its `addons21/` directory
- Reference implementation: ../autodefine_oxfordlearnersdictionaries

### Configuration

**`config.json`** - Default addon configuration:

```json
{
  "field_mapping": {
    "chinese_field": "Chinese",
    "pinyin_field": "Pinyin",
    "vietnamese_field": "Vietnamese",
    "audio_field": "Audio"
  },
  "shortcuts": {
    "auto_define_shortcut": "Ctrl+Alt+D"
  }
}
```

Users can customize these settings through Anki's Tools > Add-ons > Config interface.

### Code Style Guidelines

- **Newspaper structure**: High-level methods before low-level methods
- **Top-level imports**: Prefer top-level imports unless avoiding circular dependencies
- **Type annotations**: Use type hints throughout (Python 3.12+ syntax)
- **Descriptive names**: Prefer good function/variable names over comments
- **Comments**: Only for explaining decisions or complex algorithms

## Key Technical Considerations

### Dependencies and Compatibility

- **Python version**: Requires Python 3.12+ (uses modern type syntax)
- **Anki API compatibility**: Targets Anki 24.0.0+ (uses aqt, anki modules)
- **Core dependencies**:
  - `anki>=24.0.0` - Anki backend library
  - `aqt>=24.0.0` - Anki Qt UI library
  - `beautifulsoup4>=4.12.0` - HTML parsing
  - `soupsieve` - CSS selectors for BeautifulSoup (auto-installed)
  - `typing-extensions` - Type hint extensions (vendored)

### Dependency Vendoring

**Why vendor dependencies?**

- Anki runs in an isolated Python environment
- Users may not have pip access or technical knowledge to install dependencies
- Ensures the addon works out-of-the-box after installation

**Build process** (automated by `scripts/build.py`):

1. Copies addon Python files from `src/autodefine_cn_vn/`
2. Installs beautifulsoup4, soupsieve, and typing-extensions to `vendor/` directory using exact versions from `uv.lock`
3. Cleans up `.dist-info`, `.egg-info`, and `__pycache__` files
4. Packages everything into `.ankiaddon` file (zip format)

**Vendor path setup** (in `__init__.py`):

```python
vendor_dir = Path(__file__).parent / "vendor"
if vendor_dir.exists() and str(vendor_dir) not in sys.path:
    sys.path.insert(0, str(vendor_dir))
```

### Network Operations

- **Synchronous HTTP**: Uses `urllib.request` (not async) since Anki editor hooks are synchronous
- **Timeout handling**: Configurable timeout (default: 10 seconds)
- **Error handling**: Catches `urllib.error.HTTPError` and `urllib.error.URLError`
- **User feedback**: Shows error messages via tooltips with 5-second duration
- **URL encoding**: Chinese characters are automatically URL-encoded by `urllib`

### Anki Editor Integration

- **Hook system**: Uses `setupEditorButtons` hook to add custom button
- **Field access**: Uses Anki's field map to get/set fields by name (not by index)
- **Note updates**: Calls `editor.loadNote()` after field changes to refresh UI
- **Save handling**: Uses `editor.saveNow()` callback to ensure note is saved before processing

### Error Handling Strategy

- **Network failures**: Display user-friendly error messages, don't crash Anki
- **Missing fields**: Show configuration warning if field name doesn't exist in note type
- **No data found**: Inform user when dictionary has no entry for the word
- **Parsing errors**: Catch and display unexpected errors without breaking editor

### Testing

- **Test coverage**: 99% code coverage (see htmlcov/ directory)
- **Test structure**:
  - `tests/conftest.py` - Shared fixtures and mocks
  - `tests/test_config_manager.py` - Configuration tests
  - `tests/test_fetcher.py` - Web scraping and parsing tests
  - `tests/test_ui_hooks.py` - Editor integration tests
  - `tests/test_utils.py` - Utility function tests
  - `tests/data/` - Real HTML samples from vndic.net for testing
- **Mocking**: Uses unittest.mock to mock Anki APIs (mw, editor, note, etc.)

## Translation Data Source

The addon fetches Vietnamese translations from: `http://2.vndic.net/index.php?word={}&dict=cn_vi`
There are examples in `tests/assets/`

**Parsing strategy:**

1. **Pinyin**: Extracted from `<FONT COLOR=#7F0000>` tag, stripped of square brackets
2. **Vietnamese definition**: Finds `<img src="...CB1FF077.png">` marker, then extracts text from next `<td>` sibling

**Example HTML structure:**

```html
<font color="#7F0000">[nǐmen]</font>
<!-- Pinyin -->
<img src="img/dict/CB1FF077.png" />
<!-- Marker -->
<td>các bạn, các anh, các chị</td>
<!-- Vietnamese -->
```

## Build and Release Process

### Building the Addon

```bash
just build  # Creates dist/autodefine_cn_vn-{version}.ankiaddon
```

The build script (`scripts/build.py`):

1. Reads version from `pyproject.toml`
2. Creates temporary build directory
3. Copies Python files and config.json
4. Installs vendored dependencies from `uv.lock`
5. Cleans unnecessary files
6. Creates zip file with `.ankiaddon` extension

### Release Process

```bash
just release-patch    # 0.1.2 -> 0.1.3
just release-minor    # 0.1.2 -> 0.2.0
just release-major    # 0.1.2 -> 1.0.0
```

The release script (`scripts/release.py`):

1. Validates version format
2. Updates `pyproject.toml`
3. Updates `manifest.json` (if exists)
4. Commits changes with version message
5. Creates git tag
6. Updates CHANGELOG.md

## Manual Testing

### Setting Up Development Environment

1. Find Anki's addon directory: Open Anki > Tools > Add-ons > View Files
2. Create symlink to development directory:
   ```bash
   # Example (adjust paths for your system):
   ln -s ~/workplace/autodefine-cn-vn/src/autodefine_cn_vn \
         ~/.local/share/Anki2/addons21/autodefine_cn_vn
   ```
3. Restart Anki

### Running Anki for Testing

```bash
# Linux
/usr/local/bin/anki -p Test

# macOS
/Applications/Anki.app/Contents/MacOS/anki -p Test
```

**Tips:**

- Create a "Test" profile for safer experimentation
- Run from terminal to see stdout/stderr output (useful for debugging with `print()`)
- The addon will reload automatically when you restart Anki

## Reference Implementation

This addon is inspired by [AutoDefine Oxford Learners Dictionaries](https://github.com/artyompetrov/AutoDefine_oxfordlearnersdictionaries), which provides a similar auto-definition workflow for English vocabulary.
