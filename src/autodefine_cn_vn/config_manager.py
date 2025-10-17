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


DEFAULT_API_SETTINGS = ApiSettings(
    source="http://2.vndic.net/index.php?word={}&dict=cn_vi",
    timeout_seconds=10,
    max_retries=3,
)


@dataclass(frozen=True)
class Config:
    """Complete addon configuration."""

    version: str
    field_mapping: FieldMapping
    shortcuts: Shortcuts
    api_settings: ApiSettings


class ConfigManager:
    """Manages addon configuration using Anki's config API."""

    def __init__(self):
        """Initialize the config manager and load configuration."""
        self._config: Config = self._load_config()

    def get_config(self) -> Config:
        """Get complete configuration.

        Returns:
            Complete configuration object.
        """
        return self._config

    def get_field_mapping(self) -> FieldMapping:
        """Get field mapping configuration.

        Returns:
            Field mapping configuration object.
        """
        return self._config.field_mapping

    def get_shortcuts(self) -> Shortcuts:
        """Get keyboard shortcut configuration.

        Returns:
            Shortcuts configuration object.
        """
        return self._config.shortcuts

    def get_api_settings(self) -> ApiSettings:
        """Get API settings configuration.

        Returns:
            API settings configuration object.
        """
        return self._config.api_settings

    def reload_config(self) -> None:
        """Reload configuration from Anki's addon manager."""
        self._config = self._load_config()

    def _load_config(self) -> Config:
        """Load configuration from Anki's addon manager.

        Returns:
            Configuration object constructed from addon settings.
        """
        addon_name = __name__.split(".")[0]
        config_dict = mw.addonManager.getConfig(addon_name)

        if not config_dict:
            raise ValueError("Failed to load configuration for AutoDefine CN-VN addon.")

        return Config(
            version=config_dict["version"],
            field_mapping=FieldMapping(**config_dict["field_mapping"]),
            shortcuts=Shortcuts(**config_dict["shortcuts"]),
            api_settings=DEFAULT_API_SETTINGS,
        )
