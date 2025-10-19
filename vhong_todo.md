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

- [x] Parse sample sentences
- [x] Add one sample sentence to the card
- [x] Highlighting the chinese word

### 0.2.x: Clean up

- [x] An issue with word 斯 (xi), 讨厌
- [x] Notify should get the previous line number as well
- [x] Upgrade version of anki and aqt to 25.9.x
- [x] Add multiple sample sentences
- [ ] Add multiple definitions
- [ ] Allow empty "field" for optional configs such as audio and sample sentences
- [ ] Fix shortcut
- [ ] Separate fetcher and parser
- [ ] Add justfile command to link to addonfolder on mac
- [x] Add justfile command to build and run launcher script

### 0.2.x: Support multiple definitions

- [ ] Parse all definitions
- [ ] Pass all of them into the field

## 0.x: Nice to have features

- [ ] Have a nice icon for the button
- [ ] Add a default card type
- [ ] Support default tags such as "language::chinese" as well
- [ ] Make this more generic for different dictionary_sources (not just chinese vietnamese)
- [ ] Support multiple card types

### Won't do

- [ ] Make ConfigManager a singleton
- [ ] Create a hook so that when the config is edited in Anki UI, run ConfigManager.load_config again
