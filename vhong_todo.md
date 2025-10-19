# Anki Auto-Define Chinese-Vietnamese Addon - Todo List

### 0.2.x: Clean up

- [ ] Fix shortcut
- [ ] Parser logic should have sub-functions like parse_pinyin, parse_vietnamese etc.
- [ ] DictionaryContent values can be optional
- [ ] Use dataclass instead of DictionaryContent

## 0.3.0: Release prep

### 0.3.x: Branding

- [ ] Find a good name for the addin
- [ ] Have a nice icon for the button
- [ ] Documentation for the configuration
- [ ] Create a documentation page (e.g., readthedoc)

### 0.3.x: Contribution

- [ ] Create a contribution guide

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
