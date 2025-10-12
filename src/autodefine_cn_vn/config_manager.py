"""Configuration manager for AutoDefine Chinese-Vietnamese addon."""

from typing import Any

from aqt import mw

# Default configuration values as fallback
DEFAULT_CONFIG = {
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


class ConfigManager:
    """Manages addon configuration using Anki's config API."""

    def __init__(self):
        """Initialize the config manager and load configuration."""
        self._config = self._load_config()

    def get_field_mapping(self) -> dict[str, str]:
        """Get field mapping configuration.

        Returns:
            Dictionary mapping internal field names to Anki field names.
        """
        return self._get_with_default("field_mapping", DEFAULT_CONFIG["field_mapping"])

    def get_shortcuts(self) -> dict[str, str]:
        """Get keyboard shortcut configuration.

        Returns:
            Dictionary of shortcut names to key combinations.
        """
        return self._get_with_default("shortcuts", DEFAULT_CONFIG["shortcuts"])

    def get_api_settings(self) -> dict[str, Any]:
        """Get API settings configuration.

        Returns:
            Dictionary containing API source URL, timeout, and retry settings.
        """
        return self._get_with_default("api_settings", DEFAULT_CONFIG["api_settings"])

    def reload_config(self) -> None:
        """Reload configuration from Anki's addon manager."""
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from Anki's addon manager.

        Returns:
            Configuration dictionary
        """
        addon_name = __name__.split(".")[0]
        config = mw.addonManager.getConfig(addon_name)

        if not config:
            raise ValueError("Failed to load configuration for AutoDefine CN-VN addon.")

        return config

    def _get_with_default(self, key: str, default: Any) -> Any:
        """Get a config value with a default fallback.

        Args:
            key: Configuration key to retrieve
            default: Default value if key is missing

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
