"""
AutoDefine Chinese-Vietnamese Anki Addon

This addon automatically populates Chinese vocabulary cards with Vietnamese translations,
pinyin pronunciation, definitions, and audio pronunciation.
"""

from anki.hooks import addHook
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

__version__ = "1.0.0"
__author__ = "Vy Hong"


def on_addon_loaded():
    """Initialize the addon when Anki loads."""
    # TODO: Initialize configuration manager
    # TODO: Setup UI hooks for card editor
    # TODO: Register keyboard shortcuts
    showInfo("AutoDefine Chinese-Vietnamese addon loaded successfully!")


def setup_menu():
    """Setup addon menu in Anki's Tools menu."""
    action = QAction("AutoDefine CN-VN Settings", mw)
    action.triggered.connect(show_settings)
    mw.form.menuTools.addAction(action)


def show_settings():
    """Show addon configuration dialog."""
    # TODO: Implement settings dialog
    showInfo("Settings dialog will be implemented in future tasks.")


# Initialize addon when Anki profile is loaded
addHook("profileLoaded", on_addon_loaded)

# Setup menu when main window is available
if mw:
    setup_menu()
