import pyquoks.managers.config


class ConfigManager(pyquoks.managers.config.ConfigManager):
    settings: SettingsConfig


class SettingsConfig(pyquoks.managers.config.Config):
    _SECTION = "Settings"

    admins_list: list
    file_logging: bool
    skip_updates: bool
    workbook_extension: str
