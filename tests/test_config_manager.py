"""Tests for ConfigManager module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.config_manager import ConfigManager


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


class TestConfigManager:
    """Test suite for ConfigManager."""

    def test_init_loads_config(self, mock_mw):
        """Test that ConfigManager loads config on initialization."""
        config_manager = ConfigManager()
        mock_mw.addonManager.getConfig.assert_called_once_with("autodefine_cn_vn")
        assert config_manager._config is not None

    def test_init_raises_error_on_none_config(self, mock_mw):
        """Test that ConfigManager raises ValueError when config is None."""
        mock_mw.addonManager.getConfig.return_value = None
        with pytest.raises(ValueError, match="Failed to load configuration"):
            ConfigManager()

    def test_get_field_mapping_returns_correct_values(self, mock_mw):
        """Test that get_field_mapping returns the correct field mapping."""
        config_manager = ConfigManager()
        field_mapping = config_manager.get_field_mapping()

        assert field_mapping.chinese_field == "Chinese"
        assert field_mapping.pinyin_field == "Pinyin"
        assert field_mapping.vietnamese_field == "Vietnamese"
        assert field_mapping.audio_field == "Audio"
        assert field_mapping.sentence_field == "Sentence"

    def test_get_shortcuts_returns_correct_values(self, mock_mw):
        """Test that get_shortcuts returns the correct shortcuts."""
        config_manager = ConfigManager()
        shortcuts = config_manager.get_shortcuts()

        assert shortcuts.auto_define_shortcut == "Ctrl+Alt+D"

    def test_get_api_settings_returns_correct_values(self, mock_mw):
        """Test that get_api_settings returns the correct API settings."""
        config_manager = ConfigManager()
        api_settings = config_manager.get_api_settings()

        assert api_settings.source == "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        assert api_settings.timeout_seconds == 10
        assert api_settings.max_retries == 3

    def test_reload_config_refreshes_from_anki(self, mock_mw):
        """Test that reload_config refreshes config from Anki."""
        config_manager = ConfigManager()
        initial_call_count = mock_mw.addonManager.getConfig.call_count

        # Simulate external config change
        mock_mw.addonManager.getConfig.return_value = {
            "version": "v1",
            "field_mapping": {
                "chinese_field": "UpdatedChinese",
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

        config_manager.reload_config()

        assert mock_mw.addonManager.getConfig.call_count == initial_call_count + 1
        assert config_manager._config.field_mapping.chinese_field == "UpdatedChinese"

    def test_optional_fields_default_to_none(self, mock_mw):
        """Test that optional fields default to None when not provided in config."""
        mock_mw.addonManager.getConfig.return_value = {
            "version": "v1",
            "field_mapping": {
                "chinese_field": "Chinese",
            },
            "shortcuts": {"auto_define_shortcut": "Ctrl+Alt+D"},
        }

        config_manager = ConfigManager()
        field_mapping = config_manager.get_field_mapping()

        assert field_mapping.chinese_field == "Chinese"
        assert field_mapping.pinyin_field is None
        assert field_mapping.vietnamese_field is None
        assert field_mapping.audio_field is None
        assert field_mapping.sentence_field is None
