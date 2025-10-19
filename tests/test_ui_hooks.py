"""Tests for UI hooks module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.ui_hooks import init_ui_hooks, setup_editor_buttons


@pytest.fixture
def mock_mw():
    """Mock Anki's main window."""
    mw = MagicMock()
    mw.addonManager.getConfig.return_value = {
        "version": "v1",
        "field_mapping": {
            "chinese_field": "Chinese",
            "pinyin_field": "Pinyin",
            "vietnamese_field": "Vietnamese",
            "audio_field": "Audio",
            "sentence_field": "Sentence",
        },
        "shortcuts": {"auto_define_shortcut": "Ctrl+Alt+D"},
        "api_settings": {
            "source": "http://2.vndic.net/index.php?word={}&dict=cn_vi",
            "timeout_seconds": 10,
            "max_retries": 3,
        },
    }

    with patch("autodefine_cn_vn.config_manager.mw", mw):
        yield mw


@pytest.fixture
def mock_editor(mock_mw):
    """Mock Anki editor instance."""
    editor = MagicMock()

    # Mock note with fields
    note = MagicMock()
    note.fields = ["你好", "", "", "", ""]  # Chinese, Pinyin, Vietnamese, Audio, Sentence
    editor.note = note

    # Mock editor methods
    editor.addButton = MagicMock(return_value="mock_button")
    editor.loadNote = MagicMock()
    editor.saveNow = MagicMock(side_effect=lambda func: func())

    return editor


class TestSetupEditorButtons:
    """Tests for setup_editor_buttons function."""

    def test_adds_button_to_editor(self, mock_editor):
        """Test that setup_editor_buttons adds a button to the editor."""
        buttons = []

        result = setup_editor_buttons(buttons, mock_editor)

        assert len(result) == 1
        assert result[0] == "mock_button"
        mock_editor.addButton.assert_called_once()

    def test_button_has_correct_properties(self, mock_editor):
        """Test that the added button has correct properties."""
        buttons = []

        setup_editor_buttons(buttons, mock_editor)

        call_args = mock_editor.addButton.call_args
        assert call_args[1]["cmd"] == "autodefine_cn_vn"
        assert "Ctrl+Alt+D" in call_args[1]["tip"]
        assert call_args[1]["keys"] == "Ctrl+Alt+D"
        assert call_args[1]["label"] == "自動"


class TestInitUiHooks:
    """Tests for init_ui_hooks function."""

    def test_registers_setup_editor_buttons_hook(self):
        """Test that init_ui_hooks registers the setupEditorButtons hook."""
        with patch("autodefine_cn_vn.ui_hooks.addHook") as mock_add_hook:
            init_ui_hooks()

            mock_add_hook.assert_called_once_with("setupEditorButtons", setup_editor_buttons)
