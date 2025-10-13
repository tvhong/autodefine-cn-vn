"""Tests for UI hooks module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.ui_hooks import (
    auto_define,
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

    # Mock field_map for utils.py functions
    # field_map returns a dict: {field_name: (index, field_obj)}
    mw.col.models.field_map.return_value = {
        "Chinese": (0, MagicMock()),
        "Pinyin": (1, MagicMock()),
        "Vietnamese": (2, MagicMock()),
        "Audio": (3, MagicMock()),
    }

    with patch("autodefine_cn_vn.config_manager.mw", mw), patch("autodefine_cn_vn.utils.mw", mw):
        yield mw


@pytest.fixture
def mock_editor(mock_mw):
    """Mock Anki editor instance."""
    editor = MagicMock()

    # Mock note with fields
    note = MagicMock()
    note.fields = ["你好", "", "", ""]  # Chinese, Pinyin, Vietnamese, Audio
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
        # Change field_map so Chinese field doesn't exist (raises KeyError)
        mock_mw.col.models.field_map.return_value = {
            "Word": (0, MagicMock()),
            "Definition": (1, MagicMock()),
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

    def test_handles_field_not_found(self, mock_editor, mock_mw):
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


class TestAutoDefine:
    """Tests for auto_define function."""

    def test_fills_fields_with_fetched_data(self, mock_editor):
        """Test that auto_define fills fields with data fetched from the dictionary."""
        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.parse_dictionary_content") as mock_parse,
            patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip,
        ):
            mock_fetch.return_value = "<html>dictionary content</html>"
            mock_parse.return_value = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

            auto_define(mock_editor)

            # Check that fields were filled with fetched data
            assert mock_editor.note.fields[1] == "nǐhǎo"
            assert mock_editor.note.fields[2] == "xin chào"

            # Check that success tooltip was shown
            mock_tooltip.assert_called_once()
            assert "Successfully filled" in mock_tooltip.call_args[0][0]
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_shows_error_when_no_chinese_text(self, mock_editor):
        """Test that auto_define shows error when no Chinese text found."""
        mock_editor.note.fields[0] = ""  # Empty Chinese field

        with patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip:
            auto_define(mock_editor)

            mock_tooltip.assert_called_once()
            assert "No Chinese text" in mock_tooltip.call_args[0][0]

    def test_shows_warning_when_no_data_found(self, mock_editor):
        """Test that auto_define shows warning when no data is found."""
        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.parse_dictionary_content") as mock_parse,
            patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip,
        ):
            mock_fetch.return_value = "<html>empty content</html>"
            mock_parse.return_value = {"pinyin": "", "vietnamese": ""}

            auto_define(mock_editor)

            # Check that warning tooltip was shown
            mock_tooltip.assert_called_once()
            assert "No data found" in mock_tooltip.call_args[0][0]
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_handles_http_error(self, mock_editor):
        """Test that auto_define handles HTTP errors gracefully."""
        import urllib.error

        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip,
        ):
            mock_fetch.side_effect = urllib.error.HTTPError(
                url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
            )

            auto_define(mock_editor)

            # Check that error tooltip was shown
            mock_tooltip.assert_called_once()
            assert "HTTP error 404" in mock_tooltip.call_args[0][0]
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_handles_url_error(self, mock_editor):
        """Test that auto_define handles network errors gracefully."""
        import urllib.error

        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip,
        ):
            mock_fetch.side_effect = urllib.error.URLError("Connection refused")

            auto_define(mock_editor)

            # Check that error tooltip was shown
            mock_tooltip.assert_called_once()
            assert "Network error" in mock_tooltip.call_args[0][0]
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_handles_unexpected_error(self, mock_editor):
        """Test that auto_define handles unexpected errors gracefully."""
        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.tooltip") as mock_tooltip,
        ):
            mock_fetch.side_effect = Exception("Unexpected error")

            auto_define(mock_editor)

            # Check that error tooltip was shown
            mock_tooltip.assert_called_once()
            assert "Unexpected error" in mock_tooltip.call_args[0][0]
            assert "你好" in mock_tooltip.call_args[0][0]

    def test_uses_correct_url_and_timeout(self, mock_editor):
        """Test that auto_define uses correct URL and timeout from config."""
        with (
            patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock_fetch,
            patch("autodefine_cn_vn.ui_hooks.parse_dictionary_content") as mock_parse,
            patch("autodefine_cn_vn.ui_hooks.tooltip"),
        ):
            mock_fetch.return_value = "<html>content</html>"
            mock_parse.return_value = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

            auto_define(mock_editor)

            # Verify fetch_webpage was called with correct arguments
            expected_url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
            mock_fetch.assert_called_once_with(expected_url, 10)


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
