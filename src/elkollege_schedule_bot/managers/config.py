import pyquoks


class ConfigManager(pyquoks.managers.config.ConfigManager):
    settings: SettingsConfig


class SettingsConfig(pyquoks.managers.config.Config):
    _SECTION = "Settings"

    _VALUES = {
        "admins_list": list,
        "file_logging": bool,
        "skip_updates": bool,
        "workbook_extension": str,
    }

    admins_list: list
    file_logging: bool
    skip_updates: bool
    workbook_extension: str
