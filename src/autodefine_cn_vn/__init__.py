"""
AutoDefine Chinese-Vietnamese Anki Addon

This addon automatically populates Chinese vocabulary cards with Vietnamese translations,
pinyin pronunciation, definitions, and audio pronunciation.
"""

import sys
from pathlib import Path

# Add vendor directory to sys.path for bundled dependencies (bs4, soupsieve, etc.)
vendor_dir = Path(__file__).parent / "vendor"
if vendor_dir.exists() and str(vendor_dir) not in sys.path:
    sys.path.insert(0, str(vendor_dir))

from anki.hooks import addHook  # noqa: E402
from aqt import mw  # noqa: E402
from aqt.qt import QAction  # noqa: E402
from aqt.utils import showInfo  # noqa: E402

from autodefine_cn_vn.ui_hooks import init_ui_hooks  # noqa: E402


def on_addon_loaded():
    """Initialize the addon when Anki loads."""
    # Initialize UI hooks for card editor
    init_ui_hooks()


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
