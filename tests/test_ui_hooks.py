"""Tests for UI hooks module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.config_manager import FieldMapping
from autodefine_cn_vn.ui_hooks import (
    auto_define,
    fill_audio_field,
    fill_pinyin_field,
    fill_sentence_field,
    fill_vietnamese_field,
    get_chinese_text,
    init_ui_hooks,
    insert_into_field,
    setup_editor_buttons,
)


def get_field_mapping() -> FieldMapping:
    """Return field mapping configuration for tests."""
    return FieldMapping(
        chinese_field="Chinese",
        pinyin_field="Pinyin",
        vietnamese_field="Vietnamese",
        audio_field="Audio",
        sentence_field="Sentence",
    )


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

    # Mock field_map for utils.py functions
    # field_map returns a dict: {field_name: (index, field_obj)}
    mw.col.models.field_map.return_value = {
        "Chinese": (0, MagicMock()),
        "Pinyin": (1, MagicMock()),
        "Vietnamese": (2, MagicMock()),
        "Audio": (3, MagicMock()),
        "Sentence": (4, MagicMock()),
    }

    with patch("autodefine_cn_vn.config_manager.mw", mw), patch("autodefine_cn_vn.utils.mw", mw):
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
        with patch("autodefine_cn_vn.ui_hooks.notify") as mock_notify:
            insert_into_field(mock_editor, "text", "NonExistentField", overwrite=True)

            mock_notify.assert_called_once()
            assert "not found" in mock_notify.call_args[0][0].lower()
            mock_editor.loadNote.assert_not_called()

    def test_returns_early_when_no_note(self, mock_mw):
        """Test that insert_into_field returns early when editor has no note."""
        editor = MagicMock()
        editor.note = None

        insert_into_field(editor, "text", "Pinyin", overwrite=True)

        # Should not raise an error, just return early


class TestFillPinyinField:
    """Tests for fill_pinyin_field helper function."""

    def test_fills_pinyin_field_when_present(self, mock_editor):
        """Test that fill_pinyin_field fills the pinyin field when data is present."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

        result = fill_pinyin_field(mock_editor, parsed_data, get_field_mapping())

        assert result is True
        assert mock_editor.note.fields[1] == "nǐhǎo"
        mock_editor.loadNote.assert_called_once()

    def test_returns_false_when_pinyin_empty(self, mock_editor):
        """Test that fill_pinyin_field returns False when pinyin is empty."""
        parsed_data = {"pinyin": "", "vietnamese": "xin chào"}

        result = fill_pinyin_field(mock_editor, parsed_data, get_field_mapping())

        assert result is False
        mock_editor.loadNote.assert_not_called()

    def test_returns_false_when_pinyin_missing(self, mock_editor):
        """Test that fill_pinyin_field returns False when pinyin key is missing."""
        parsed_data = {"vietnamese": "xin chào"}

        result = fill_pinyin_field(mock_editor, parsed_data, get_field_mapping())

        assert result is False
        mock_editor.loadNote.assert_not_called()


class TestFillVietnameseField:
    """Tests for fill_vietnamese_field helper function."""

    def test_fills_vietnamese_field_when_present(self, mock_editor):
        """Test that fill_vietnamese_field fills the vietnamese field when data is present."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

        result = fill_vietnamese_field(mock_editor, parsed_data, get_field_mapping())

        assert result is True
        assert mock_editor.note.fields[2] == "xin chào"
        mock_editor.loadNote.assert_called_once()

    def test_returns_false_when_vietnamese_empty(self, mock_editor):
        """Test that fill_vietnamese_field returns False when vietnamese is empty."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": ""}

        result = fill_vietnamese_field(mock_editor, parsed_data, get_field_mapping())

        assert result is False
        mock_editor.loadNote.assert_not_called()

    def test_returns_false_when_vietnamese_missing(self, mock_editor):
        """Test that fill_vietnamese_field returns False when vietnamese key is missing."""
        parsed_data = {"pinyin": "nǐhǎo"}

        result = fill_vietnamese_field(mock_editor, parsed_data, get_field_mapping())

        assert result is False
        mock_editor.loadNote.assert_not_called()


class TestFillSentenceField:
    """Tests for fill_sentence_field helper function."""

    def test_fills_sentence_field_when_present(self, mock_editor):
        """Test that fill_sentence_field fills the sentence field when sentences are present."""
        parsed_data = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
            "sentences": [
                {"chinese": "你好吗？", "vietnamese": "Bạn khỏe không?"},
                {"chinese": "你好世界。", "vietnamese": "Xin chào thế giới."},
            ],
        }

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "你好")

        assert result is True
        assert mock_editor.note.fields[4] == "<b>你好</b>吗？"
        mock_editor.loadNote.assert_called_once()

    def test_fills_only_chinese_sentence(self, mock_editor):
        """Test that fill_sentence_field fills only Chinese text without Vietnamese."""
        parsed_data = {"sentences": [{"chinese": "你们好。", "vietnamese": "Xin chào các bạn."}]}

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "你们")

        assert result is True
        assert mock_editor.note.fields[4] == "<b>你们</b>好。"
        assert "Xin chào" not in mock_editor.note.fields[4]
        assert "<br>" not in mock_editor.note.fields[4]

    def test_uses_first_sentence_only(self, mock_editor):
        """Test that fill_sentence_field uses only the first sentence."""
        parsed_data = {
            "sentences": [
                {"chinese": "第一句。", "vietnamese": "Câu thứ nhất."},
                {"chinese": "第二句。", "vietnamese": "Câu thứ hai."},
            ]
        }

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "第一")

        assert result is True
        assert mock_editor.note.fields[4] == "<b>第一</b>句。"
        assert "第二句" not in mock_editor.note.fields[4]
        assert "Câu thứ" not in mock_editor.note.fields[4]

    def test_highlights_word_when_appears_multiple_times(self, mock_editor):
        """Test that fill_sentence_field highlights all occurrences of the word."""
        parsed_data = {
            "sentences": [{"chinese": "我我我很好。", "vietnamese": "Tôi tôi tôi rất khỏe."}]
        }

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "我")

        assert result is True
        assert mock_editor.note.fields[4] == "<b>我</b><b>我</b><b>我</b>很好。"
        mock_editor.loadNote.assert_called_once()

    def test_returns_false_when_sentences_empty(self, mock_editor):
        """Test that fill_sentence_field returns False when sentences list is empty."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào", "sentences": []}

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "你好")

        assert result is False
        mock_editor.loadNote.assert_not_called()

    def test_returns_false_when_sentences_missing(self, mock_editor):
        """Test that fill_sentence_field returns False when sentences key is missing."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

        result = fill_sentence_field(mock_editor, parsed_data, get_field_mapping(), "你好")

        assert result is False
        mock_editor.loadNote.assert_not_called()


class TestFillAudioField:
    """Tests for fill_audio_field helper function."""

    def test_downloads_and_fills_audio_field_when_present(self, mock_editor):
        """Test that fill_audio_field downloads and fills audio when URL is present."""
        parsed_data = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
            "audio_url": "http://example.com/audio.mp3",
        }

        with patch("autodefine_cn_vn.ui_hooks.download_audio") as mock_download_audio:
            mock_download_audio.return_value = "autodefine_cn_vn_你好.mp3"

            result = fill_audio_field(
                mock_editor,
                parsed_data,
                get_field_mapping(),
                "你好",
                "http://2.vndic.net/index.php?word={}&dict=cn_vi",
                10,
            )

            assert result is True
            assert mock_editor.note.fields[3] == "[sound:autodefine_cn_vn_你好.mp3]"
            mock_editor.loadNote.assert_called_once()
            mock_download_audio.assert_called_once_with(
                mock_editor.note,
                "http://example.com/audio.mp3",
                "你好",
                "http://2.vndic.net/index.php?word={}&dict=cn_vi",
                10,
            )

    def test_returns_false_when_audio_url_empty(self, mock_editor):
        """Test that fill_audio_field returns False when audio URL is empty."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào", "audio_url": ""}

        result = fill_audio_field(
            mock_editor,
            parsed_data,
            get_field_mapping(),
            "你好",
            "http://2.vndic.net/index.php?word={}&dict=cn_vi",
            10,
        )

        assert result is False
        mock_editor.loadNote.assert_not_called()

    def test_returns_false_when_audio_url_missing(self, mock_editor):
        """Test that fill_audio_field returns False when audio_url key is missing."""
        parsed_data = {"pinyin": "nǐhǎo", "vietnamese": "xin chào"}

        result = fill_audio_field(
            mock_editor,
            parsed_data,
            get_field_mapping(),
            "你好",
            "http://2.vndic.net/index.php?word={}&dict=cn_vi",
            10,
        )

        assert result is False
        mock_editor.loadNote.assert_not_called()

    def test_returns_false_when_no_note(self, mock_mw):
        """Test that fill_audio_field returns False when editor has no note."""
        editor = MagicMock()
        editor.note = None

        parsed_data = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
            "audio_url": "http://example.com/audio.mp3",
        }

        result = fill_audio_field(
            editor,
            parsed_data,
            get_field_mapping(),
            "你好",
            "http://2.vndic.net/index.php?word={}&dict=cn_vi",
            10,
        )

        assert result is False

    def test_returns_false_and_notifies_when_download_fails(self, mock_editor):
        """Test that fill_audio_field returns False and shows notification when download fails."""
        parsed_data = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
            "audio_url": "http://example.com/audio.mp3",
        }

        with (
            patch("autodefine_cn_vn.ui_hooks.download_audio") as mock_download_audio,
            patch("autodefine_cn_vn.ui_hooks.notify") as mock_notify,
        ):
            mock_download_audio.side_effect = Exception("Download failed")

            result = fill_audio_field(
                mock_editor,
                parsed_data,
                get_field_mapping(),
                "你好",
                "http://2.vndic.net/index.php?word={}&dict=cn_vi",
                10,
            )

            assert result is False
            mock_notify.assert_called_once()
            assert "Could not download audio" in mock_notify.call_args[0][0]
            mock_editor.loadNote.assert_not_called()


@pytest.fixture
def mock_fetch_webpage():
    """Mock fetch_webpage function."""
    with patch("autodefine_cn_vn.ui_hooks.fetch_webpage") as mock:
        yield mock


@pytest.fixture
def mock_parse_dictionary_content():
    """Mock parse_dictionary_content function."""
    with patch("autodefine_cn_vn.ui_hooks.parse_dictionary_content") as mock:
        yield mock


@pytest.fixture
def mock_notify():
    """Mock notify function."""
    with patch("autodefine_cn_vn.ui_hooks.notify") as mock:
        yield mock


class TestAutoDefine:
    """Tests for auto_define function."""

    def test_fills_fields_with_fetched_data(
        self, mock_editor, mock_fetch_webpage, mock_parse_dictionary_content, mock_notify
    ):
        """Test that auto_define fills fields with data fetched from the dictionary."""
        mock_fetch_webpage.return_value = "<html>dictionary content</html>"
        mock_parse_dictionary_content.return_value = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
        }

        auto_define(mock_editor)

        # Check that fields were filled with fetched data
        assert mock_editor.note.fields[1] == "nǐhǎo"
        assert mock_editor.note.fields[2] == "xin chào"

        # Check that success notification was shown
        mock_notify.assert_called_once()
        assert "Successfully filled" in mock_notify.call_args[0][0]
        assert "你好" in mock_notify.call_args[0][0]

    def test_shows_error_when_no_chinese_text(self, mock_editor, mock_notify):
        """Test that auto_define shows error when no Chinese text found."""
        mock_editor.note.fields[0] = ""  # Empty Chinese field

        auto_define(mock_editor)

        mock_notify.assert_called_once()
        assert "No Chinese text" in mock_notify.call_args[0][0]

    def test_shows_warning_when_no_data_found(
        self, mock_editor, mock_fetch_webpage, mock_parse_dictionary_content, mock_notify
    ):
        """Test that auto_define shows warning when no data is found."""
        mock_fetch_webpage.return_value = "<html>empty content</html>"
        mock_parse_dictionary_content.return_value = {"pinyin": "", "vietnamese": ""}

        auto_define(mock_editor)

        # Check that warning notification was shown
        mock_notify.assert_called_once()
        assert "No data found" in mock_notify.call_args[0][0]
        assert "你好" in mock_notify.call_args[0][0]

    def test_handles_http_error(self, mock_editor, mock_fetch_webpage, mock_notify):
        """Test that auto_define handles HTTP errors gracefully."""
        import urllib.error

        mock_fetch_webpage.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        auto_define(mock_editor)

        # Check that error notification was shown
        mock_notify.assert_called_once()
        assert "HTTP error 404" in mock_notify.call_args[0][0]
        assert "你好" in mock_notify.call_args[0][0]

    def test_handles_url_error(self, mock_editor, mock_fetch_webpage, mock_notify):
        """Test that auto_define handles network errors gracefully."""
        import urllib.error

        mock_fetch_webpage.side_effect = urllib.error.URLError("Connection refused")

        auto_define(mock_editor)

        # Check that error notification was shown
        mock_notify.assert_called_once()
        assert "Network error" in mock_notify.call_args[0][0]
        assert "你好" in mock_notify.call_args[0][0]

    def test_handles_unexpected_error(self, mock_editor, mock_fetch_webpage, mock_notify):
        """Test that auto_define handles unexpected errors gracefully."""
        mock_fetch_webpage.side_effect = Exception("Unexpected error")

        auto_define(mock_editor)

        # Check that error notification was shown
        mock_notify.assert_called_once()
        assert "Unexpected error" in mock_notify.call_args[0][0]
        assert "你好" in mock_notify.call_args[0][0]

    def test_uses_correct_url_and_timeout(
        self, mock_editor, mock_fetch_webpage, mock_parse_dictionary_content, mock_notify
    ):
        """Test that auto_define uses correct URL and timeout from config."""
        mock_fetch_webpage.return_value = "<html>content</html>"
        mock_parse_dictionary_content.return_value = {
            "pinyin": "nǐhǎo",
            "vietnamese": "xin chào",
        }

        auto_define(mock_editor)

        # Verify fetch_webpage was called with correct arguments
        expected_url = "http://2.vndic.net/index.php?word=%E4%BD%A0%E5%A5%BD&dict=cn_vi"
        mock_fetch_webpage.assert_called_once_with(expected_url, 10)


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
