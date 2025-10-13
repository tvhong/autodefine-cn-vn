"""UI hooks for integrating with Anki's card editor."""

import urllib.error
from typing import TYPE_CHECKING

from anki.hooks import addHook
from anki.notes import Note

from autodefine_cn_vn.config_manager import ConfigManager
from autodefine_cn_vn.fetcher import fetch_webpage, format_url, parse_dictionary_content
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
    shortcut = shortcuts["auto_define_shortcut"]

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
    url_template = str(api_settings["source"])
    timeout = int(api_settings["timeout_seconds"])
    url = format_url(url_template, chinese_text)

    try:
        html_content = fetch_webpage(url, timeout)
        parsed_data = parse_dictionary_content(html_content)

        # Fill pinyin field
        pinyin = parsed_data.get("pinyin", "")
        if pinyin:
            insert_into_field(
                editor,
                pinyin,
                field_mapping["pinyin_field"],
                overwrite=True,
            )

        # Fill Vietnamese field
        vietnamese = parsed_data.get("vietnamese", "")
        if vietnamese:
            insert_into_field(
                editor,
                vietnamese,
                field_mapping["vietnamese_field"],
                overwrite=True,
            )

        if pinyin or vietnamese:
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


def get_chinese_text(editor: "Editor") -> str:
    """Extract Chinese text from the configured source field.

    Args:
        editor: Anki editor instance

    Returns:
        str: Chinese text from the configured field
    """
    config_manager = ConfigManager()
    field_mapping = config_manager.get_field_mapping()
    chinese_field_name = field_mapping["chinese_field"]

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
