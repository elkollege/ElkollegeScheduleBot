import datetime

import aiogram
import aiogram.fsm.state
import aiogram.utils.keyboard
import pyquoks
import schedule_parser


class States(aiogram.fsm.state.StatesGroup):
    upload_schedule = aiogram.fsm.state.State()


# region Providers

class StringsProvider(pyquoks.data.StringsProvider):
    class AlertStrings(pyquoks.data.StringsProvider.Strings):
        @classmethod
        def export_logs_unavailable(cls) -> str:
            return "Логирование отключено!"

        @classmethod
        def button_unavailable(cls) -> str:
            return "Эта кнопка недоступна!"

        @classmethod
        def schedule_unavailable(cls) -> str:
            return "Расписание недоступно!"

        @classmethod
        def schedule_deleted(cls) -> str:
            return "Расписание удалено!"

    class ButtonStrings(pyquoks.data.StringsProvider.Strings):

        # region /start

        @classmethod
        def schedule(cls) -> str:
            return "Расписание"

        @classmethod
        def select_group(cls) -> str:
            return "Выбрать группу"

        @classmethod
        def settings(cls) -> str:
            return "Настройки"

        # endregion

        # region /admin

        @classmethod
        def manage_schedule(cls) -> str:
            return "Расписание"

        @classmethod
        def upload_schedule(cls) -> str:
            return "Загрузить"

        @classmethod
        def delete_schedule(cls) -> str:
            return "Удалить"

        @classmethod
        def manage_substitutions(cls) -> str:
            return "Замены"

        @classmethod
        def export_logs(cls) -> str:
            return "Экспортировать логи"

        # endregion

        # region back_to_*

        @classmethod
        def back(cls) -> str:
            return "Назад"

        @classmethod
        def cancel(cls) -> str:
            return "Отмена"

        # endregion

    class MenuStrings(pyquoks.data.StringsProvider.Strings):

        # region /start

        @classmethod
        def start(cls, user: aiogram.types.User) -> str:
            return (
                f"<b>Привет, {user.full_name}!</b>\n"
                f"\n"
                f"Здесь вы можете посмотреть\n"
                f"актуальное расписание\n"
                f"Электростальский колледжа\n"
                f"для вашей учебной группы."
            )

        # endregion

        # region /admin

        @classmethod
        def admin(cls, user: aiogram.types.User, time_started: datetime.datetime) -> str:
            return (
                f"<b>Меню администратора</b>\n"
                f"\n"
                f"Добро пожаловать, {user.full_name}!\n"
                f"\n"
                f"Дата запуска: <b>{time_started.astimezone(datetime.UTC).strftime("%d.%m.%y %H:%M:%S")} UTC</b>"
            )

        @classmethod
        def manage_schedule(cls, schedule_availability: bool) -> str:
            return (
                f"<b>Управление расписанием</b>\n"
                f"\n"
                f"Статус расписания: <b>{"Загружено" if schedule_availability else "Отсутствует"}</b>"
            )

        @classmethod
        def upload_schedule(cls, schedule_extension: str) -> str:
            return (
                f"<b>Загрузка расписания</b>\n"
                f"\n"
                f"Отправьте файл с расширением <b>\".{schedule_extension}\"</b>"
            )

        @classmethod
        def upload_schedule_error(cls) -> str:
            return (
                f"<b>Возникла ошибка!</b>\n"
                f"\n"
                f"Не удалось обработать расписание."
            )

        @classmethod
        def upload_schedule_success(cls, groups_count: int) -> str:
            return (
                f"<b>Расписание загружено!</b>\n"
                f"\n"
                f"Кол-во учебных групп: <b>{groups_count}</b>"
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
    def __init__(self, strings_provider: StringsProvider) -> None:
        self._strings = strings_provider

    # region /start

    def schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.schedule(),
            callback_data="schedule",
        )

    def select_group(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.select_group(),
            callback_data="select_group",
        )

    def settings(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.settings(),
            callback_data="settings",
        )

    # endregion

    # region /admin

    def manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.manage_schedule(),
            callback_data="manage_schedule",
        )

    def manage_substitutions(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.manage_substitutions(),
            callback_data="manage_substitutions",
        )

    def export_logs(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.export_logs(),
            callback_data="export_logs",
        )

    def upload_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.upload_schedule(),
            callback_data="upload_schedule",
        )

    def delete_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.delete_schedule(),
            callback_data="delete_schedule",
        )

    # endregion

    # region back_to_*

    def back_to_start(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="start",
        )

    def back_to_admin(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="admin",
        )

    def back_to_manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="manage_schedule",
        )

    def cancel_to_manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data="manage_schedule",
        )

    # endregion


class KeyboardsProvider:
    def __init__(self, buttons_provider: ButtonsProvider) -> None:
        self._buttons = buttons_provider

    # region /start

    def start(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.schedule())
        markup_builder.row(self._buttons.select_group(), self._buttons.settings())

        return markup_builder.as_markup()

    # endregion

    # region /admin

    def admin(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.manage_schedule(), self._buttons.manage_substitutions())
        markup_builder.row(self._buttons.export_logs())

        return markup_builder.as_markup()

    def manage_schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.upload_schedule(), self._buttons.delete_schedule())
        markup_builder.row(self._buttons.back_to_admin())

        return markup_builder.as_markup()

    def upload_schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.cancel_to_manage_schedule())

        return markup_builder.as_markup()

    def upload_schedule_ended(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.back_to_manage_schedule())

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
            "workbook_extension": str,
        }

        admins_list: list
        bot_token: str
        file_logging: bool
        skip_updates: bool
        workbook_extension: str

    _OBJECTS = {
        "settings": SettingsConfig,
    }

    settings: SettingsConfig


class DataManager(pyquoks.data.DataManager):
    _OBJECTS = {
        "schedule": list[schedule_parser.models.GroupSchedule],
    }

    schedule: list[schedule_parser.models.GroupSchedule]


# endregion

# region Services

class LoggerService(pyquoks.data.LoggerService):
    def log_user_interaction(self, user: aiogram.types.User, interaction: str) -> None:
        user_info = f"@{user.username} ({user.id})" if user.username else user.id
        self.info(f"{user_info} - \"{interaction}\"")

# endregion
