"""Tests for utility functions."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.utils import get_field, set_field


@pytest.fixture
def mock_mw():
    """Mock Anki's main window and collection."""
    with patch("autodefine_cn_vn.utils.mw") as mw:
        # Mock the field_map method
        mw.col.models.field_map.return_value = {
            "Chinese": (0, {}),
            "Pinyin": (1, {}),
            "Vietnamese": (2, {}),
            "Audio": (3, {}),
        }
        yield mw


@pytest.fixture
def mock_note():
    """Mock Anki note instance."""
    note = MagicMock()
    note.fields = ["你好", "nǐ hǎo", "xin chào", "[sound:audio.mp3]"]
    note.note_type.return_value = MagicMock()  # Mock note type/model
    return note


class TestGetField:
    """Tests for get_field function."""

    def test_gets_field_value_by_name(self, mock_mw, mock_note):
        """Test that get_field returns the correct field value."""
        result = get_field(mock_note, "Chinese")
        assert result == "你好"

    def test_gets_different_field_values(self, mock_mw, mock_note):
        """Test that get_field can retrieve different field values."""
        assert get_field(mock_note, "Chinese") == "你好"
        assert get_field(mock_note, "Pinyin") == "nǐ hǎo"
        assert get_field(mock_note, "Vietnamese") == "xin chào"
        assert get_field(mock_note, "Audio") == "[sound:audio.mp3]"

    def test_calls_note_type_method(self, mock_mw, mock_note):
        """Test that get_field calls note.note_type() to get the model."""
        get_field(mock_note, "Chinese")
        mock_note.note_type.assert_called_once()

    def test_calls_field_map_with_model(self, mock_mw, mock_note):
        """Test that get_field calls field_map with the note's model."""
        model = mock_note.note_type.return_value
        get_field(mock_note, "Chinese")
        mock_mw.col.models.field_map.assert_called_once_with(model)

    def test_raises_key_error_for_nonexistent_field(self, mock_mw, mock_note):
        """Test that get_field raises KeyError for nonexistent field."""
        with pytest.raises(KeyError):
            get_field(mock_note, "NonExistentField")


class TestSetField:
    """Tests for set_field function."""

    def test_sets_field_value_by_name(self, mock_mw, mock_note):
        """Test that set_field sets the correct field value."""
        set_field(mock_note, "Pinyin", "new pinyin")
        assert mock_note.fields[1] == "new pinyin"

    def test_overwrites_existing_value(self, mock_mw, mock_note):
        """Test that set_field overwrites existing field value."""
        original = mock_note.fields[0]
        assert original == "你好"

        set_field(mock_note, "Chinese", "新词")
        assert mock_note.fields[0] == "新词"

    def test_sets_different_fields(self, mock_mw, mock_note):
        """Test that set_field can set different fields."""
        set_field(mock_note, "Chinese", "word1")
        set_field(mock_note, "Vietnamese", "word2")
        set_field(mock_note, "Audio", "word3")

        assert mock_note.fields[0] == "word1"
        assert mock_note.fields[2] == "word2"
        assert mock_note.fields[3] == "word3"

    def test_calls_note_type_method(self, mock_mw, mock_note):
        """Test that set_field calls note.note_type() to get the model."""
        set_field(mock_note, "Chinese", "test")
        mock_note.note_type.assert_called_once()

    def test_calls_field_map_with_model(self, mock_mw, mock_note):
        """Test that set_field calls field_map with the note's model."""
        model = mock_note.note_type.return_value
        set_field(mock_note, "Chinese", "test")
        mock_mw.col.models.field_map.assert_called_once_with(model)

    def test_raises_key_error_for_nonexistent_field(self, mock_mw, mock_note):
        """Test that set_field raises KeyError for nonexistent field."""
        with pytest.raises(KeyError):
            set_field(mock_note, "NonExistentField", "value")
