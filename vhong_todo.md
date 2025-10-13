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

### 0.1.2: Pull definition from remote website

- [x] Download the webpage from api_settings.source (with {} replaced with the chinese word) into memory
- [x] Parse pinyin, and Vietnamese definition from it
- [x] Add additioonal test data: http://2.vndic.net/index.php?word=%E4%BD%A0%E4%BB%AC&dict=cn_vi
- [x] Package bs4 into the release somehow
- [x] Fill out fields with pinyin and Vietnamese definition
- [x] Download the data and parse

### 0.1.3: Clean up

- [ ] Update claude.md
- [ ] Make ConfigManager a singleton
- [ ] Create a hook so that when the config is edited in Anki UI, run ConfigManager.load_config again

## 0.2.0: Support audio

- [ ] Download the audio into appropriate places
  - Example: http://2.vndic.net/index.php?word=%E4%BD%A0%E4%BB%AC&dict=cn_vi
- [ ] Link it to the card

### 0.1.x: Clean up

- [ ] Use a typed class for config
- [ ] Remove retry config

### 0.1.x: Support sample sentences

- [ ] Add configuration field
- [ ] Parse sample sentences
- [ ] Add multiple sentences to the fields, highlighting the chinese word

### 0.1.x: Support multiple definitions

- [ ] Parse all definitions
- [ ] Pass all of them into the field

## 0.x: Nice to have features

- [ ] Have a nice icon
- [ ] Support default tags such as "language::chinese" as well
- [ ] Make this more generic for different type of translators
