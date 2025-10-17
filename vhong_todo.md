# Anki Auto-Define Chinese-Vietnamese Addon - Todo List

## 0.2.0: Support audio and sample sentences

- [x] Download the audio into appropriate places
  - Example: http://2.vndic.net/index.php?word=%E4%BD%A0%E4%BB%AC&dict=cn_vi
- [x] Link it to the card

### 0.2.1: Clean up

- [x] Use a typed class for config
- [x] Add a version field for config
- [x] Remove retry config

### 0.2.x: Support sample sentences

- [ ] Add configuration field
- [ ] Parse sample sentences
- [ ] Add multiple sentences to the fields, highlighting the chinese word

### 0.2.x: Support multiple definitions

- [ ] Parse all definitions
- [ ] Pass all of them into the field

## 0.x: Nice to have features

- [ ] Have a nice icon
- [ ] Support default tags such as "language::chinese" as well
- [ ] Make this more generic for different types of translators
- [ ] Support multiple card types
- [ ] Fix shortcut

### Won't do

- [ ] Make ConfigManager a singleton
- [ ] Create a hook so that when the config is edited in Anki UI, run ConfigManager.load_config again
