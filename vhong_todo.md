# Anki Auto-Define Chinese-Vietnamese Addon - Todo List

## 0.1.0: Project Setup & Core Structure

- [x] **Task 1**: Setup project structure and manifest - Create addon structure with manifest.json, **init**.py
- [x] **Task 2**: Setup lint and test using uv
- [x] **Task 3**: Implement basic configuration system - Create config.json, config_manager.py for user settings
- [x] **Task 4**: Setup Anki UI hooks - Implement ui_hooks.py to integrate with Anki's card editor to add a button that will trigger auto filling of the configured fields with some stub values.

### 0.1.1: Clean up

- [x] Check tests for ui_hooks
- [x] Make ui_hooks a class?
- [x] Create field utility functions (get_field, set_field) with tests

## 0.2: Pull definition from remote website

### 0.2.1: Clean up

- [ ] Make ConfigManager a singleton
- [ ] Create a hook so that when the config is edited, run ConfigManager.load_config again

## 0.3: Nice to have features

- [ ] Support default tags such as "language::chinese" as well
- [ ] Make this more generic for different type of translators
- [ ] Have a nice icon
