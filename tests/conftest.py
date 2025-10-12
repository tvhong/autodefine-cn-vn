"""Test configuration and shared fixtures."""

import sys
from unittest.mock import MagicMock

# Mock Anki modules before any imports
sys.modules["anki"] = MagicMock()
sys.modules["anki.hooks"] = MagicMock()
sys.modules["anki.notes"] = MagicMock()
sys.modules["aqt"] = MagicMock()
sys.modules["aqt.qt"] = MagicMock()
sys.modules["aqt.utils"] = MagicMock()
