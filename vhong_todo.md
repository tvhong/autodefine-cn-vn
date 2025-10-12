# Anki Auto-Define Chinese-Vietnamese Addon - Todo List

## Phase 1: Project Setup & Core Structure

- [ ] **Task 1**: Setup project structure and manifest - Create addon structure with manifest.json, **init**.py
- [ ] **Task 2**: Implement basic configuration system - Create config.json, config_manager.py for user settings
- [ ] **Task 3**: Setup Anki UI hooks - Implement ui_hooks.py to integrate with Anki's card editor
- [ ] **Task 4**: Create a build system to build a release package that's consumable by Anki

## Phase 2: Translation Core

- [ ] **Task 4**: Implement Chinese text processor - Create text_processor.py for Chinese character handling
- [ ] **Task 5**: Build Chinese dictionary service - Implement chinese_dict.py for word lookup and definitions
- [ ] **Task 6**: Build Vietnamese translation service - Implement vietnamese_dict.py for CN→VN translation
- [ ] **Task 7**: Create core translator module - Implement translator.py orchestrating translation workflow

## Phase 3: Anki Integration

- [ ] **Task 8**: Implement field manager - Create field_manager.py for automatic field population
- [ ] **Task 9**: Add audio service support - Implement audio_service.py for pronunciation audio
- [ ] **Task 10**: Create user configuration UI - Add Anki addon config interface for field mapping

## Phase 4: Testing & Polish

- [ ] **Task 11**: Write comprehensive tests - Implement unit tests for all core modules
- [ ] **Task 12**: Add error handling and logging - Robust error handling for network/parsing failures
- [ ] **Task 13**: Performance optimization - Optimize for large vocabulary sets and fast response
- [ ] **Task 14**: Documentation and packaging - README, user guide, and distribution preparation

## Reference Project

Based on: https://github.com/artyompetrov/AutoDefine_oxfordlearnersdictionaries

## Project Structure

```
autodefine-cn-vn/
├── manifest.json                 # Addon metadata and distribution config
├── __init__.py                   # Main addon entry point
├── config.json                   # Default configuration
├── config.md                     # Configuration documentation
├── core/
│   ├── __init__.py
│   ├── translator.py            # Translation logic (Chinese to Vietnamese)
│   ├── field_manager.py         # Anki field population logic
│   └── ui_hooks.py              # Anki UI integration hooks
├── services/
│   ├── __init__.py
│   ├── chinese_dict.py          # Chinese dictionary lookup
│   ├── vietnamese_dict.py       # Vietnamese translation service
│   └── audio_service.py         # Audio pronunciation fetching
├── utils/
│   ├── __init__.py
│   ├── text_processor.py        # Text processing utilities
│   └── config_manager.py        # Configuration management
└── tests/
    ├── test_translator.py
    ├── test_field_manager.py
    └── test_integration.py
```

## Key Features

- **Auto-fill on vocabulary input**: Detect Chinese text input and auto-populate fields
- **Configurable field mapping**: Users can map which fields get populated
- **Multiple data sources**: Chinese definitions, Vietnamese translations, pinyin, audio
- **Keyboard shortcuts**: Quick activation (Ctrl+Alt+D for auto-define)
- **Offline capability**: Cache translations for offline use
- **Custom note types**: Provide pre-configured Chinese-Vietnamese note templates

## Current Status: Ready to start Task 1

