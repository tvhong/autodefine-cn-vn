# AutoDefine Chinese-Vietnamese for Anki

An Anki addon that automatically fills card fields with Chinese word definitions, Vietnamese translations, pinyin, and audio pronunciations when you enter Chinese vocabulary.

## Features

- **Automatic Field Population**: Enter Chinese text and automatically get definitions, translations, and pronunciations
- **Chinese to Vietnamese Translation**: Native support for Chinese-Vietnamese language pairs
- **Multiple Data Sources**:
  - Chinese definitions and explanations
  - Vietnamese translations
  - Pinyin romanization
  - Audio pronunciations
- **Configurable Field Mapping**: Customize which fields get populated with what data
- **Keyboard Shortcuts**: Quick activation with `Ctrl+Alt+D`
- **Custom Note Types**: Pre-configured templates optimized for Chinese-Vietnamese learning

## Installation

1. Download the latest release from [Releases](../../releases)
2. In Anki, go to `Tools` ’ `Add-ons` ’ `Install from file...`
3. Select the downloaded `.ankiaddon` file
4. Restart Anki

## Configuration

After installation:

1. Go to `Tools` ’ `Add-ons`
2. Select "AutoDefine Chinese-Vietnamese"
3. Click `Config` to customize:
   - Field mappings
   - Translation sources
   - Keyboard shortcuts
   - Cache settings

## Usage

### Basic Usage

1. Create or edit a card with Chinese vocabulary
2. Enter Chinese text in your designated input field
3. Press `Ctrl+Alt+D` or use the auto-trigger feature
4. Watch as definitions, translations, and pronunciations are automatically filled

## Field Mapping

Default field configuration:

- **Chinese**: Source vocabulary field
- **Vietnamese**: Vietnamese translation
- **Pinyin**: Romanized pronunciation
- **Audio**: Pronunciation audio file

## Development

### Requirements

- Python 3.11+
- Anki 2.1.x

### Setup

```bash
git clone https://github.com/yourusername/autodefine-cn-vn.git
cd autodefine-cn-vn
uv sync
```

### Testing

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Inspired by [AutoDefine Oxford Learners Dictionaries](https://github.com/artyompetrov/AutoDefine_oxfordlearnersdictionaries)
- Built for the Anki spaced repetition system

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues or have suggestions:

- Open an [Issue](../../issues)
- Check the [Wiki](../../wiki) for troubleshooting
- Join discussions in [Discussions](../../discussions)

---

**Note**: This addon is currently under development. Please report any bugs or feature requests through GitHub Issues.

