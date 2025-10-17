"""Configuration manager for AutoDefine Chinese-Vietnamese addon."""

from dataclasses import dataclass

from aqt import mw


@dataclass(frozen=True)
class FieldMapping:
    """Field name mappings for Anki note fields."""

    chinese_field: str
    pinyin_field: str
    vietnamese_field: str
    audio_field: str


@dataclass(frozen=True)
class Shortcuts:
    """Keyboard shortcut configurations."""

    auto_define_shortcut: str


@dataclass(frozen=True)
class ApiSettings:
    """API settings for fetching definitions."""

    source: str
    timeout_seconds: int
    max_retries: int


@dataclass(frozen=True)
class Config:
    """Complete addon configuration."""

    field_mapping: FieldMapping
    shortcuts: Shortcuts
    api_settings: ApiSettings


class ConfigManager:
    """Manages addon configuration using Anki's config API."""

    def __init__(self):
        """Initialize the config manager and load configuration."""
        self._config: dict[str, dict[str, str | int]] = self._load_config()

    def get_field_mapping(self) -> dict[str, str]:
        """Get field mapping configuration.

        Returns:
            Dictionary mapping internal field names to Anki field names.
        """
        return cast(dict[str, str], self._config["field_mapping"])

    def get_shortcuts(self) -> dict[str, str]:
        """Get keyboard shortcut configuration.

        Returns:
            Dictionary of shortcut names to key combinations.
        """
        return cast(dict[str, str], self._config["shortcuts"])

    def get_api_settings(self) -> dict[str, str | int]:
        """Get API settings configuration.

        Returns:
            Dictionary containing API source URL, timeout, and retry settings.
        """
        return self._config["api_settings"]

    def reload_config(self) -> None:
        """Reload configuration from Anki's addon manager."""
        self._config = self._load_config()

    def _load_config(self) -> dict[str, dict[str, str | int]]:
        """Load configuration from Anki's addon manager.

        Returns:
            Configuration dictionary
        """
        addon_name = __name__.split(".")[0]
        config = mw.addonManager.getConfig(addon_name)

        if not config:
            raise ValueError("Failed to load configuration for AutoDefine CN-VN addon.")

        return config
