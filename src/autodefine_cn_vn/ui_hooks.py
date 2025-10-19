"""UI hooks for integrating with Anki's card editor."""

from typing import TYPE_CHECKING

from anki.hooks import addHook

from autodefine_cn_vn.auto_fill import auto_fill
from autodefine_cn_vn.config_manager import ConfigManager

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
        func=lambda ed: ed.saveNow(lambda: auto_fill(ed)),
        tip=f"AutoDefine Chinese-Vietnamese ({shortcut if shortcut else 'no shortcut'})",
        label="自動",  # "Auto" in Chinese
        keys=shortcut if shortcut else "",
    )

    buttons.append(button)
    return buttons
