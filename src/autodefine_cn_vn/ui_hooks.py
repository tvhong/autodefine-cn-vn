"""UI hooks for integrating with Anki's card editor."""

import urllib.error
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from anki.hooks import addHook
from anki.notes import Note

from autodefine_cn_vn.config_manager import ConfigManager, FieldMapping
from autodefine_cn_vn.fetcher import (
    DictionaryContent,
    fetch_audio,
    fetch_webpage,
    format_url,
    parse_dictionary_content,
)
from autodefine_cn_vn.utils import get_field, notify, set_field

if TYPE_CHECKING:
    from aqt.editor import Editor


def init_ui_hooks() -> None:
    """Initialize UI hooks for the addon."""
    addHook("setupEditorButtons", setup_editor_buttons)


def setup_editor_buttons(buttons: list[str], editor: "Editor") -> list[str]:
    """Add AutoDefine button to the Anki editor.

    Args:
        buttons: List of editor buttons
        editor: Anki editor instance

    Returns:
        list: Updated list of buttons
    """
    config_manager = ConfigManager()
    shortcuts = config_manager.get_shortcuts()
    shortcut = shortcuts.auto_define_shortcut

    button = editor.addButton(
        icon=None,
        cmd="autodefine_cn_vn",
        func=lambda ed: ed.saveNow(lambda: auto_define(ed)),
        tip=f"AutoDefine Chinese-Vietnamese ({shortcut if shortcut else 'no shortcut'})",
        label="自動",  # "Auto" in Chinese
        keys=shortcut if shortcut else "",
    )

    buttons.append(button)
    return buttons


def auto_define(editor: "Editor") -> None:
    """Auto-fill fields with fetched pinyin and Vietnamese definition.

    Fetches the Chinese-Vietnamese dictionary page for the Chinese text
    and populates the card fields with pinyin and Vietnamese definition.

    Args:
        editor: Anki editor instance
    """
    # Get Chinese text from source field
    chinese_text = get_chinese_text(editor)

    if not chinese_text:
        notify("AutoDefine: No Chinese text found in source field.")
        return

    config_manager = ConfigManager()
    field_mapping = config_manager.get_field_mapping()
    api_settings = config_manager.get_api_settings()

    # Format URL and fetch webpage
    url_template = api_settings.source
    timeout = api_settings.timeout_seconds
    url = format_url(url_template, chinese_text)

    try:
        html_content = fetch_webpage(url, timeout)
        parsed_data = parse_dictionary_content(html_content)

        # Fill fields using helper methods
        pinyin_filled = fill_pinyin_field(editor, parsed_data, field_mapping)
        vietnamese_filled = fill_vietnamese_field(editor, parsed_data, field_mapping)
        sentence_filled = fill_sentence_field(editor, parsed_data, field_mapping, chinese_text)
        _ = fill_audio_field(
            editor, parsed_data, field_mapping, chinese_text, url_template, timeout
        )

        if pinyin_filled or vietnamese_filled or sentence_filled:
            notify(f"AutoDefine: Successfully filled fields for '{chinese_text}'")
        else:
            notify(
                f"AutoDefine: No data found for '{chinese_text}'. "
                f"The word may not exist in the dictionary."
            )

    except urllib.error.HTTPError as e:
        notify(
            f"AutoDefine: HTTP error {e.code} while fetching data for '{chinese_text}'",
            period=5000,
        )
    except urllib.error.URLError as e:
        notify(
            f"AutoDefine: Network error while fetching data for '{chinese_text}': {e.reason}",
            period=5000,
        )
    except Exception as e:
        notify(
            f"AutoDefine: Unexpected error while processing '{chinese_text}': {str(e)}",
            period=5000,
        )


def fill_pinyin_field(
    editor: "Editor", parsed_data: DictionaryContent, field_mapping: FieldMapping
) -> bool:
    """Fill pinyin field from parsed data.

    Args:
        editor: Anki editor instance
        parsed_data: DictionaryContent containing parsed data
        field_mapping: Field mapping configuration object

    Returns:
        bool: True if pinyin was filled, False otherwise
    """
    # Skip if field not configured
    if not field_mapping.pinyin_field:
        return False

    pinyin = parsed_data.get("pinyin", "")
    if pinyin:
        insert_into_field(
            editor,
            pinyin,
            field_mapping.pinyin_field,
            overwrite=True,
        )
        return True
    return False


def fill_vietnamese_field(
    editor: "Editor", parsed_data: DictionaryContent, field_mapping: FieldMapping
) -> bool:
    """Fill vietnamese field from parsed data.

    Args:
        editor: Anki editor instance
        parsed_data: DictionaryContent containing parsed data
        field_mapping: Field mapping configuration object

    Returns:
        bool: True if vietnamese was filled, False otherwise
    """
    # Skip if field not configured
    if not field_mapping.vietnamese_field:
        return False

    vietnamese = parsed_data.get("vietnamese", "")
    if vietnamese:
        insert_into_field(
            editor,
            vietnamese,
            field_mapping.vietnamese_field,
            overwrite=True,
        )
        return True
    return False


def fill_sentence_field(
    editor: "Editor",
    parsed_data: DictionaryContent,
    field_mapping: FieldMapping,
    chinese_word: str,
) -> bool:
    """Fill sentence field with all sample sentences from parsed data.

    Args:
        editor: Anki editor instance
        parsed_data: DictionaryContent containing parsed data including sentences
        field_mapping: Field mapping configuration object
        chinese_word: Chinese word being learned to highlight in sentence

    Returns:
        bool: True if sentence was filled, False otherwise
    """
    # Skip if field not configured
    if not field_mapping.sentence_field:
        return False

    sentences = parsed_data.get("sentences", [])
    if not sentences:
        return False

    highlighted_sentences = []
    for sentence in sentences:
        chinese = sentence.get("chinese", "")
        if chinese:
            # Highlight the Chinese word being learned with <b> tags
            highlighted_sentence = chinese.replace(chinese_word, f"<b>{chinese_word}</b>")
            highlighted_sentences.append(highlighted_sentence)

    if highlighted_sentences:
        # Join multiple sentences with <br> tags
        combined_sentences = "<br>".join(highlighted_sentences)
        insert_into_field(
            editor,
            combined_sentences,
            field_mapping.sentence_field,
            overwrite=True,
        )
        return True

    return False


def fill_audio_field(
    editor: "Editor",
    parsed_data: DictionaryContent,
    field_mapping: FieldMapping,
    chinese_text: str,
    url_template: str,
    timeout: int,
) -> bool:
    """Download audio and fill audio field.

    Args:
        editor: Anki editor instance
        parsed_data: DictionaryContent containing parsed data including audio_url
        field_mapping: Field mapping configuration object
        chinese_text: Chinese text used for filename generation
        url_template: Template URL to extract base URL from
        timeout: Timeout for audio download in seconds

    Returns:
        bool: True if audio was filled, False otherwise
    """
    # Skip if field not configured
    if not field_mapping.audio_field:
        return False

    audio_url = parsed_data.get("audio_url", "")
    if not audio_url or not editor.note:
        return False

    try:
        filename = download_audio(
            editor.note,
            audio_url,
            chinese_text,
            url_template,
            timeout,
        )
        # Insert audio reference into audio field
        audio_reference = f"[sound:{filename}]"
        insert_into_field(
            editor,
            audio_reference,
            field_mapping.audio_field,
            overwrite=True,
        )
        return True
    except Exception as e:
        # Don't fail the whole operation if audio download fails
        notify(
            f"AutoDefine: Warning - Could not download audio: {str(e)}",
            period=3000,
        )
        return False


def download_audio(
    note: Note,
    audio_url: str,
    chinese_text: str,
    url_template: str,
    timeout: int,
) -> str:
    """Download audio file and save to Anki's media collection.

    Args:
        note: Anki note instance
        audio_url: URL of the audio file to download
        chinese_text: Chinese text used for filename generation
        url_template: Template URL to extract base URL from
        timeout: Timeout for audio download in seconds

    Returns:
        str: Filename of the saved audio file

    Raises:
        Exception: If audio download or save fails
    """
    # Extract base URL from the source URL
    parsed_url = urlparse(url_template)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Download audio file
    audio_data = fetch_audio(audio_url, base_url, timeout)

    # Generate filename from Chinese text
    # Use sanitized filename with .mp3 extension
    safe_filename = f"autodefine_cn_vn_{chinese_text}.mp3"

    # Write audio to Anki's media collection
    filename = note.col.media.write_data(safe_filename, audio_data)

    return filename


def get_chinese_text(editor: "Editor") -> str:
    """Extract Chinese text from the configured source field.

    Args:
        editor: Anki editor instance

    Returns:
        str: Chinese text from the configured field
    """
    config_manager = ConfigManager()
    field_mapping = config_manager.get_field_mapping()
    chinese_field_name = field_mapping.chinese_field

    # Get the note and find the Chinese field
    note = editor.note
    if not note:
        return ""

    try:
        return get_field(note, chinese_field_name).strip()
    except KeyError:
        return ""


def insert_into_field(
    editor: "Editor", text: str, field_name: str, overwrite: bool = False
) -> None:
    """Insert text into a specific field by name.

    Args:
        editor: Anki editor instance
        text: Text to insert
        field_name: Name of the field to insert into
        overwrite: If True, replace existing content; if False, append
    """
    note: Note | None = editor.note
    if not note:
        return

    try:
        if overwrite:
            set_field(note, field_name, text)
        else:
            current_value = get_field(note, field_name)
            set_field(note, field_name, current_value + text)
    except KeyError:
        notify(
            f"AutoDefine: Field '{field_name}' not found in note type. "
            f"Please check your configuration.",
            period=5000,
        )
        return

    editor.loadNote()
