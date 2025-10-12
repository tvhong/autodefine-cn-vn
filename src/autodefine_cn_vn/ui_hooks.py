"""UI hooks for integrating with Anki's card editor."""

from typing import TYPE_CHECKING

from anki.hooks import addHook
from anki.notes import Note
from aqt.utils import tooltip

from autodefine_cn_vn.config_manager import ConfigManager
from autodefine_cn_vn.utils import get_field, set_field

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
        func=lambda ed: ed.saveNow(lambda: auto_define_with_stub(ed)),
        tip=f"AutoDefine Chinese-Vietnamese ({shortcut if shortcut else 'no shortcut'})",
        label="自動",  # "Auto" in Chinese
        keys=shortcut if shortcut else "",
    )

    buttons.append(button)
    return buttons


def auto_define_with_stub(editor: "Editor") -> None:
    """Auto-fill fields with stub data for testing.

    This is a temporary implementation that fills fields with placeholder data
    to test the UI integration.

    Args:
        editor: Anki editor instance
    """
    # Get Chinese text from source field
    chinese_text = get_chinese_text(editor)

    if not chinese_text:
        tooltip("AutoDefine: No Chinese text found in source field.")
        return

    config_manager = ConfigManager()
    field_mapping = config_manager.get_field_mapping()

    # Fill fields with stub data
    insert_into_field(
        editor,
        f"[Stub Pinyin for: {chinese_text}]",
        field_mapping["pinyin_field"],
        overwrite=True,
    )

    insert_into_field(
        editor,
        f"[Stub Vietnamese translation for: {chinese_text}]",
        field_mapping["vietnamese_field"],
        overwrite=True,
    )

    insert_into_field(
        editor,
        "[Stub Audio]",
        field_mapping["audio_field"],
        overwrite=True,
    )

    tooltip(f"AutoDefine: Filled fields with stub data for '{chinese_text}'")


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
        tooltip(
            f"AutoDefine: Field '{field_name}' not found in note type. "
            f"Please check your configuration.",
            period=5000,
        )
        return

    editor.loadNote()
