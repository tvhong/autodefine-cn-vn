"""Tests for UI hooks module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.ui_hooks import (
    auto_define_with_stub,
    get_chinese_text,
    init_ui_hooks,
    insert_into_field,
    setup_editor_buttons,
)


@pytest.fixture
def mock_mw():
    """Mock Anki's main window."""
    mw = MagicMock()
    mw.addonManager.getConfig.return_value = {
        "field_mapping": {
            "chinese_field": "Chinese",
            "pinyin_field": "Pinyin",
            "vietnamese_field": "Vietnamese",
            "audio_field": "Audio",
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
    note.fields = ["你好", "", "", ""]  # Chinese, Pinyin, Vietnamese, Audio
    note.model.return_value = {
        "flds": [
            {"name": "Chinese"},
            {"name": "Pinyin"},
            {"name": "Vietnamese"},
            {"name": "Audio"},
        ]
    }
    editor.note = note

    # Mock editor methods
    editor.addButton = MagicMock(return_value="mock_button")
    editor.loadNote = MagicMock()
    editor.saveNow = MagicMock(side_effect=lambda func: func())

    return editor


class TestGetChineseText:
    """Tests for get_chinese_text function."""

    def test_extracts_chinese_text_from_configured_field(self, mock_editor):
        """Test that get_chinese_text extracts text from the Chinese field."""
        chinese_text = get_chinese_text(mock_editor)
        assert chinese_text == "你好"

    def test_returns_empty_string_when_no_note(self, mock_mw):
        """Test that get_chinese_text returns empty string when editor has no note."""
        editor = MagicMock()
        editor.note = None

        chinese_text = get_chinese_text(editor)
        assert chinese_text == ""

    def test_returns_empty_string_when_field_not_found(self, mock_editor, mock_mw):
        """Test that get_chinese_text returns empty string when field is not found."""
        # Change field names so Chinese field doesn't exist
        mock_editor.note.model.return_value = {
            "flds": [
                {"name": "Word"},
                {"name": "Definition"},
            ]
        }

        chinese_text = get_chinese_text(mock_editor)
        assert chinese_text == ""


class TestInsertIntoField:
    """Tests for insert_into_field function."""

    def test_inserts_text_into_field_by_name(self, mock_editor):
        """Test that insert_into_field inserts text into the correct field."""
        insert_into_field(mock_editor, "拼音", "Pinyin", overwrite=True)

        assert mock_editor.note.fields[1] == "拼音"
        mock_editor.loadNote.assert_called_once()

    def test_appends_text_when_overwrite_false(self, mock_editor):
        """Test that insert_into_field appends text when overwrite is False."""
        mock_editor.note.fields[1] = "existing"

        insert_into_field(mock_editor, " appended", "Pinyin", overwrite=False)

        assert mock_editor.note.fields[1] == "existing appended"
        mock_editor.loadNote.assert_called_once()

    def test_overwrites_text_when_overwrite_true(self, mock_editor):
        """Test that insert_into_field overwrites text when overwrite is True."""
        mock_editor.note.fields[1] = "existing"

        insert_into_field(mock_editor, "new", "Pinyin", overwrite=True)

        assert mock_editor.note.fields[1] == "new"
        mock_editor.loadNote.assert_called_once()

    def test_handles_field_not_found(self, mock_editor):
        """Test that insert_into_field handles field not found gracefully."""
        with patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip:
            insert_into_field(mock_editor, "text", "NonExistentField", overwrite=True)

            mock_tooltip.assert_called_once()
            assert "not found" in mock_tooltip.call_args[0][0].lower()
            mock_editor.loadNote.assert_not_called()

    def test_returns_early_when_no_note(self, mock_mw):
        """Test that insert_into_field returns early when editor has no note."""
        editor = MagicMock()
        editor.note = None

        insert_into_field(editor, "text", "Pinyin", overwrite=True)

        # Should not raise an error, just return early


class TestAutoDefineWithStub:
    """Tests for auto_define_with_stub function."""

    def test_fills_fields_with_stub_data(self, mock_editor):
        """Test that auto_define_with_stub fills all configured fields with stub data."""
        with patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip:
            auto_define_with_stub(mock_editor)

            # Check that fields were filled
            assert "[Stub Pinyin for: 你好]" in mock_editor.note.fields[1]
            assert "[Stub Vietnamese translation for: 你好]" in mock_editor.note.fields[2]
            assert "[Stub Audio]" in mock_editor.note.fields[3]

            # Check that success tooltip was shown
            mock_tooltip.assert_called_once()
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_shows_error_when_no_chinese_text(self, mock_editor):
        """Test that auto_define_with_stub shows error when no Chinese text found."""
        mock_editor.note.fields[0] = ""  # Empty Chinese field

        with patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip:
            auto_define_with_stub(mock_editor)

            mock_tooltip.assert_called_once()
            assert "No Chinese text" in mock_tooltip.call_args[0][0]


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
