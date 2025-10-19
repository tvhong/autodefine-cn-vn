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
- [x] Add multiple definitions
- [x] Allow empty "field" for optional configs such as audio and sample sentences. Only require "chinese" field.
- [x] Should use `<br>` to break vietnamese definitions instead of `\n`
- [x] Separate fetcher and parser
- [ ] Parser logic should have sub-functions like parse_pinyin, parse_vietnamese etc.
- [ ] Move auto_define function into its own file, called auto_define.py or something
  - [ ] Let's find a good name for this function first
- [ ] Add justfile command to link to addonfolder on mac (link from the build folder to Mac's Application)
  - `ln -s $HOME/workplace/autodefine-cn-vn/build/autodefine_cn_vn  $HOME/Library/Application\ Support/Anki2/addons21/autodefine_cn_vn`
  - Maybe does a search in Mac's Application folder first and ask user potential locations
- [ ] Fix shortcut
- [x] Add justfile command to build and run launcher script
- [ ] DictionaryContent values can be optional
- [ ] Use dataclass instead of DictionaryContent

### 0.2.x: Support multiple definitions

- [x] Parse all definitions
- [x] Pass all of them into the field

## 0.3.0: Release prep

### 0.3.x: Branding

- [ ] Find a good name for the addin
- [ ] Have a nice icon for the button
- [ ] Documentation for the configuration
- [ ] Create a documentation page (e.g., readthedoc)

## 0.x: Nice to have features

- [ ] Support default tags such as "language::chinese" as well
- [ ] Make this more generic for different dictionary_sources (not just chinese vietnamese)
- [ ] Add a default card type via a menu?
- [ ] Support multiple card types
- [ ] Add validation (and meaningful error messages) for configuration.
- [ ] Separate this into a lib/ and a src/.

### Won't do

- [ ] Make ConfigManager a singleton
- [ ] Create a hook so that when the config is edited in Anki UI, run ConfigManager.load_config again
