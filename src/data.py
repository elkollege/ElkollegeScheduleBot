from __future__ import annotations

import datetime

import aiogram
import aiogram.utils.keyboard
import pyquoks


# region Providers

class StringsProvider(pyquoks.data.StringsProvider):
    class AlertStrings(pyquoks.data.StringsProvider.Strings):
        @property
        def export_logs_unavailable(self) -> str:
            return "Логирование отключено!"

        @property
        def button_unavailable(self) -> str:
            return "Эта кнопка недоступна!"

    class ButtonStrings(pyquoks.data.StringsProvider.Strings):

        # region /admin

        @property
        def add_schedule(self) -> str:
            return "Добавить расписание"

        @property
        def add_substitutions(self) -> str:
            return "Добавить замены"

        @property
        def export_logs(self) -> str:
            return "Экспортировать логи"

        # endregion

    class MenuStrings(pyquoks.data.StringsProvider.Strings):

        # region /admin

        @staticmethod
        def admin(user: aiogram.types.User, time_started: datetime.datetime) -> str:
            return (
                f"<b>Меню администратора</b>\n"
                f"\n"
                f"Добро пожаловать, {user.full_name}!\n"
                f"\n"
                f"Дата запуска: <b>{time_started.astimezone(datetime.UTC).strftime("%d.%m.%y %H:%M:%S")} UTC</b>"
            )

        # endregion

    _OBJECTS = {
        "alert": AlertStrings,
        "button": ButtonStrings,
        "menu": MenuStrings,
    }

    alert: AlertStrings
    button: ButtonStrings
    menu: MenuStrings


class ButtonsProvider:
    def __init__(self, strings: StringsProvider, config: ConfigManager) -> None:
        self._strings = strings
        self._config = config

    # region /admin

    @property
    def add_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.add_schedule,
            callback_data="add_schedule",
        )

    @property
    def add_substitutions(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.add_substitutions,
            callback_data="add_substitutions",
        )

    @property
    def export_logs(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.export_logs,
            callback_data="export_logs",
        )

    # endregion


class KeyboardProvider:
    def __init__(self, buttons: ButtonsProvider) -> None:
        self._buttons = buttons

    # region /admin

    @property
    def admin(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.add_schedule, self._buttons.add_substitutions)
        markup_builder.row(self._buttons.export_logs)

        return markup_builder.as_markup()

    # endregion


# endregion

# region Managers

class ConfigManager(pyquoks.data.ConfigManager):
    class SettingsConfig(pyquoks.data.ConfigManager.Config):
        _SECTION = "Settings"

        _VALUES = {
            "admins_list": list,
            "bot_token": str,
            "file_logging": bool,
            "skip_updates": bool,
        }

        admins_list: list
        bot_token: str
        file_logging: bool
        skip_updates: bool

    _OBJECTS = {
        "settings": SettingsConfig,
    }

    settings: SettingsConfig


# endregion

# region Services

class LoggerService(pyquoks.data.LoggerService):
    def log_user_interaction(self, user: aiogram.types.User, interaction: str) -> None:
        user_info = f"@{user.username} ({user.id})" if user.username else user.id
        self.info(f"{user_info} - \"{interaction}\"")

# endregion
