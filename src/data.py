import datetime
import itertools
import json
import math
import os
import textwrap

import aiogram
import aiogram.fsm.state
import aiogram.utils.keyboard
import pyquoks
import schedule_parser

import constants
import models
import utils


# region States

class States(aiogram.fsm.state.StatesGroup):
    upload_schedule = aiogram.fsm.state.State()
    upload_substitutions = aiogram.fsm.state.State()


# endregion

# region Providers

class EnvironmentProvider(pyquoks.data.EnvironmentProvider):
    TELEGRAM_BOT_TOKEN: str


class StringsProvider(pyquoks.data.StringsProvider):
    class AlertStrings(pyquoks.data.StringsProvider.Strings):

        # region /start

        @classmethod
        def group_selected(cls, group: str) -> str:
            return f"Выбрана группа \"{group}\"!"

        @classmethod
        def group_not_selected(cls) -> str:
            return "Выберите группу для просмотра расписания!"

        @classmethod
        def group_missing_in_schedule(cls) -> str:
            return "Расписание для выбранной группы отсутствует!"

        # endregion

        # region /admin

        @classmethod
        def schedule_unavailable(cls) -> str:
            return "Расписание недоступно!"

        @classmethod
        def schedule_deleted(cls) -> str:
            return "Расписание удалено!"

        @classmethod
        def substitutions_unavailable(cls) -> str:
            return "Замены недоступны!"

        @classmethod
        def substitutions_deleted(cls) -> str:
            return "Замены удалены!"

        @classmethod
        def export_logs_unavailable(cls) -> str:
            return "Логирование отключено!"

        # endregion

        @classmethod
        def button_unavailable(cls) -> str:
            return "Эта кнопка недоступна!"

    class ButtonStrings(pyquoks.data.StringsProvider.Strings):

        # region /start

        @classmethod
        def view_schedules(cls) -> str:
            return "Просмотр расписания"

        @classmethod
        def view_groups(cls) -> str:
            return "Выбрать группу"

        @classmethod
        def settings(cls) -> str:
            return "Настройки"

        @classmethod
        def settings_switch(cls, name: str, value: bool) -> str:
            return f"{name} - {"✅" if value else "❌"}"

        # endregion

        # region /admin

        @classmethod
        def schedule(cls) -> str:
            return "Расписание"

        @classmethod
        def substitutions(cls) -> str:
            return "Замены"

        @classmethod
        def upload(cls) -> str:
            return "Загрузить"

        @classmethod
        def delete(cls) -> str:
            return "Удалить"

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

        # region page_*

        @classmethod
        def page_previous(cls) -> str:
            return "<"

        @classmethod
        def page_info(cls, current_page: int, total_pages: int) -> str:
            return f"{current_page} / {total_pages}"

        @classmethod
        def page_next(cls) -> str:
            return ">"

        # endregion

    class MenuStrings(pyquoks.data.StringsProvider.Strings):

        # region /start

        @classmethod
        def start(cls, user: aiogram.types.User) -> str:
            return textwrap.dedent(
                f"""\
                <b>Привет, {user.full_name}!</b>
                
                Здесь вы можете посмотреть
                актуальное расписание
                Электростальского колледжа
                для вашей учебной группы.
                """,
            )

        @classmethod
        def view_schedules(cls) -> str:
            return textwrap.dedent(
                f"""\
                <b>Просмотр расписания</b>
                
                Выберите нужную дату:
                """,
            )

        @classmethod
        def schedule(
                cls,
                date: datetime.datetime,
                schedule: list[schedule_parser.models.Period],
                has_substitutions: bool,
        ) -> str:
            if schedule:
                readable_schedule = "\n".join(period.readable for period in schedule)
            else:
                readable_schedule = "*Пары отсутствуют*"

            # different string format is used to avoid unnecessary leading whitespaces
            return f"<b>Расписание на {utils.get_readable_date(date)}</b>{"\n*Замены не загружены*" if not has_substitutions else ""}\n\n{readable_schedule}"

        @classmethod
        def view_groups(cls) -> str:
            return textwrap.dedent(
                f"""\
                <b>Выбор группы</b>
                
                Выберите свою учебную 
                группу из списка ниже:
                """,
            )

        @classmethod
        def settings(cls, user: models.User) -> str:
            return textwrap.dedent(
                f"""\
                <b>Настройки</b>
                
                UserID: <b>{user.id}</b>
                {f"Группа: <b>{user.group}</b>" if user.group else ""}
                """,
            )

        # endregion

        # region /admin

        @classmethod
        def admin(cls, user: aiogram.types.User, time_started: datetime.datetime) -> str:
            return textwrap.dedent(
                f"""\
                <b>Меню администратора</b>
                
                Добро пожаловать, {user.full_name}!
                
                Дата запуска: <b>{time_started.astimezone(datetime.UTC).strftime("%d.%m.%y %H:%M:%S")} UTC</b>
                """,
            )

        @classmethod
        def manage_schedule(cls, schedule: list[schedule_parser.models.GroupSchedule]) -> str:
            return textwrap.dedent(
                f"""\
                <b>Управление расписанием</b>
                
                Статус расписания: <b>{"Загружено" if schedule else "Отсутствует"}</b>
                {f"Учебных групп: <b>{len(schedule)}</b>" if schedule else ""}
                """,
            )

        @classmethod
        def upload_schedule(cls, workbook_extension: str) -> str:
            return textwrap.dedent(
                f"""\
                <b>Загрузка расписания</b>
                
                Отправьте файл с расширением <b>\".{workbook_extension}\"</b>
                """,
            )

        @classmethod
        def upload_schedule_error(cls) -> str:
            return textwrap.dedent(
                f"""\
                <b>Возникла ошибка!</b>
                
                Не удалось обработать расписание.
                """,
            )

        @classmethod
        def upload_schedule_success(cls, schedule: list[schedule_parser.models.GroupSchedule]) -> str:
            return textwrap.dedent(
                f"""\
                <b>Расписание загружено!</b>
                
                Учебных групп: <b>{len(schedule)}</b>
                """,
            )

        @classmethod
        def view_substitutions(cls) -> str:
            return textwrap.dedent(
                f"""\
                <b>Управление заменами</b>
                
                Выберите нужную дату:
                """,
            )

        @classmethod
        def manage_substitutions(
                cls,
                date: datetime.datetime,
                substitutions: list[schedule_parser.models.Substitution],
        ) -> str:
            return textwrap.dedent(
                f"""\
                <b>Управление заменами на {utils.get_readable_date(date)}</b>
                
                Статус замен: <b>{"Загружены" if substitutions else "Отсутствуют"}</b>
                {f"Замен: <b>{len(substitutions)}</b>" if substitutions else ""}
                """,
            )

        @classmethod
        def upload_substitutions(cls, date: datetime.datetime, workbook_extension: str) -> str:
            return textwrap.dedent(
                f"""\
                <b>Загрузка замен на {utils.get_readable_date(date)}</b>
                
                Отправьте файл с расширением <b>\".{workbook_extension}\"</b>
                """,
            )

        @classmethod
        def upload_substitutions_error(cls) -> str:
            return textwrap.dedent(
                f"""\
                <b>Возникла ошибка!</b>
                
                Не удалось обработать замены.
                """,
            )

        @classmethod
        def upload_substitutions_success(
                cls,
                date: datetime.datetime,
                substitutions: list[schedule_parser.models.Substitution],
        ) -> str:
            return textwrap.dedent(
                f"""\
                <b>Замены на {utils.get_readable_date(date)} загружены!</b>
                
                Замен: <b>{len(substitutions)}</b>
                """,
            )

        # endregion

        # region notification_*

        @classmethod
        def notification_schedule_uploaded(cls) -> str:
            return "Загружено новое расписание!"

        @classmethod
        def notification_substitutions_uploaded(cls, date: datetime.datetime) -> str:
            return f"Загружены замены на {utils.get_readable_date(date)}!"

        # endregion

    class SettingsStrings(pyquoks.data.StringsProvider.Strings):
        @classmethod
        def is_notifiable(cls) -> str:
            return "Уведомления"

        @classmethod
        def _get_setting_string(cls, setting: str) -> str:
            string_callable = getattr(cls, setting, None)

            if string_callable is None:
                raise AttributeError(
                    name=setting,
                    obj=cls,
                )
            else:
                return string_callable()

    alert: AlertStrings
    button: ButtonStrings
    menu: MenuStrings
    settings: SettingsStrings


class ButtonsProvider:
    def __init__(self, strings_provider: StringsProvider) -> None:
        self._strings = strings_provider

    # region /start

    def view_schedules(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_schedules(),
            callback_data="view_schedules",
        )

    @staticmethod
    def schedule(date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=utils.get_readable_date(date),
            callback_data=f"schedule {utils.get_callback_date(date)}",
        )

    def view_groups(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_groups(),
            callback_data=f"view_groups {constants.FIRST_PAGE}",
        )

    @staticmethod
    def group(group: schedule_parser.models.GroupSchedule) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=group.group,
            callback_data=f"group {group.group}",
        )

    def settings(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.settings(),
            callback_data="settings",
        )

    def settings_switch(self, name: str, value: bool) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.settings_switch(
                name=self._strings.settings._get_setting_string(
                    setting=name,
                ),
                value=value,
            ),
            callback_data=f"settings_switch {name}",
        )

    # endregion

    # region /admin

    def manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.schedule(),
            callback_data="manage_schedule",
        )

    def upload_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.upload(),
            callback_data="upload_schedule",
        )

    def delete_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.delete(),
            callback_data="delete_schedule",
        )

    def view_substitutions(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.substitutions(),
            callback_data="view_substitutions",
        )

    @staticmethod
    def manage_substitutions(date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=utils.get_readable_date(date),
            callback_data=f"manage_substitutions {utils.get_callback_date(date)}",
        )

    def upload_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.upload(),
            callback_data=f"upload_substitutions {utils.get_callback_date(date)}",
        )

    def delete_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.delete(),
            callback_data=f"delete_substitutions {utils.get_callback_date(date)}",
        )

    def export_logs(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.export_logs(),
            callback_data="export_logs",
        )

    # endregion

    # region back_to_*

    def back_to_start(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="start",
        )

    def back_to_view_schedules(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="view_schedules",
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

    def back_to_view_substitutions(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data="view_substitutions",
        )

    def back_to_manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.back(),
            callback_data=f"manage_substitutions {utils.get_callback_date(date)}",
        )

    def cancel_to_manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data="manage_schedule",
        )

    def cancel_to_manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data=f"manage_substitutions {utils.get_callback_date(date)}",
        )

    # endregion

    # region _page

    def page_previous(self, callback: str, is_answer_callback: bool) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_previous(),
            callback_data="answer_callback" if is_answer_callback else callback,
        )

    def page_info(
            self,
            callback: str,
            is_answer_callback: bool,
            page_current: int,
            pages_total: int,
    ) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_info(
                current_page=page_current,
                total_pages=pages_total,
            ),
            callback_data="answer_callback" if is_answer_callback else callback,
        )

    def page_next(self, callback: str, is_answer_callback: bool) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_next(),
            callback_data="answer_callback" if is_answer_callback else callback,
        )

    # endregion

    # region notifications_*

    def view_schedule(
            self,
            date: datetime.datetime,
    ) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_schedules(),
            callback_data=f"schedule {utils.get_callback_date(date)}",
        )

    # endregion


class KeyboardsProvider:
    def __init__(self, buttons_provider: ButtonsProvider) -> None:
        self._buttons = buttons_provider

    # region Helpers

    def _get_page_buttons(
            self,
            callback: str,
            page: int,
            items_count: int,
            items_per_page: int,
    ) -> tuple[
        aiogram.types.InlineKeyboardButton,
        aiogram.types.InlineKeyboardButton,
        aiogram.types.InlineKeyboardButton,
    ]:
        pages_total = math.ceil(items_count / items_per_page)
        page_previous = page - 1
        page_next = page + 1

        return (
            self._buttons.page_previous(
                callback=f"{callback} {page_previous}",
                is_answer_callback=page_previous < constants.FIRST_PAGE,
            ),
            self._buttons.page_info(
                callback=f"{callback} {constants.FIRST_PAGE}",
                is_answer_callback=page == constants.FIRST_PAGE,
                page_current=page,
                pages_total=pages_total,
            ),
            self._buttons.page_next(
                callback=f"{callback} {page_next}",
                is_answer_callback=page_next > pages_total,
            ),
        )

    # endregion

    # region /start

    def start(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.view_schedules())
        markup_builder.row(
            self._buttons.view_groups(),
            self._buttons.settings(),
        )

        return markup_builder.as_markup()

    def view_schedules(self) -> aiogram.types.InlineKeyboardMarkup:
        current_date = datetime.datetime.now()

        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.schedule(
                    current_date + datetime.timedelta(
                        days=days_delta,
                    ),
                ) for days_delta in range(constants.SCHEDULE_DAYS)
            ],
        )
        markup_builder.row(self._buttons.back_to_start())

        return markup_builder.as_markup()

    def schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.back_to_view_schedules())

        return markup_builder.as_markup()

    def view_groups(
            self,
            groups: list[schedule_parser.models.GroupSchedule],
            page: int,
    ) -> aiogram.types.InlineKeyboardMarkup:
        buttons_index = page - 1

        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.group(group) for group in list(
                    itertools.batched(
                        groups,
                        constants.GROUPS_PER_PAGE
                    )
                )[buttons_index]
            ],
            width=constants.GROUPS_PER_ROW,
        )
        markup_builder.row(
            *self._get_page_buttons(
                callback="view_groups",
                page=page,
                items_count=len(groups),
                items_per_page=constants.GROUPS_PER_PAGE,
            ),
        )
        markup_builder.row(self._buttons.back_to_start())

        return markup_builder.as_markup()

    def settings(self, user: models.User) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.settings_switch(
                    name=setting,
                    value=getattr(user, setting)
                ) for setting in user._switchable_values()
            ],
            width=constants.SETTINGS_PER_ROW,
        )
        markup_builder.row(self._buttons.back_to_start())

        return markup_builder.as_markup()

    # endregion

    # region /admin

    def admin(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.manage_schedule(),
            self._buttons.view_substitutions(),
        )
        markup_builder.row(self._buttons.export_logs())

        return markup_builder.as_markup()

    def manage_schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.upload_schedule(),
            self._buttons.delete_schedule(),
        )
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

    def select_substitutions(self) -> aiogram.types.InlineKeyboardMarkup:
        current_date = datetime.datetime.now()

        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.manage_substitutions(
                    current_date + datetime.timedelta(
                        days=days_delta,
                    ),
                ) for days_delta in range(constants.SCHEDULE_DAYS)
            ],
        )
        markup_builder.row(self._buttons.back_to_admin())

        return markup_builder.as_markup()

    def manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.upload_substitutions(date),
            self._buttons.delete_substitutions(date),
        )
        markup_builder.row(self._buttons.back_to_view_substitutions())

        return markup_builder.as_markup()

    def upload_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.cancel_to_manage_substitutions(date))

        return markup_builder.as_markup()

    def upload_substitutions_ended(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.back_to_manage_substitutions(date))

        return markup_builder.as_markup()

    # endregion

    # region notification_*

    def notification_schedule_uploaded(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.view_schedules())

        return markup_builder.as_markup()

    def notification_substitutions_uploaded(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(self._buttons.schedule(date))

        return markup_builder.as_markup()

    # endregion


# endregion

# region Managers

class ConfigManager(pyquoks.data.ConfigManager):
    class SettingsConfig(pyquoks.data.ConfigManager.Config):
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

    settings: SettingsConfig


class DataManager(pyquoks.data.DataManager):
    schedule: list[schedule_parser.models.GroupSchedule]

    def get_substitutions(self, date: datetime.datetime) -> list[schedule_parser.models.Substitution]:
        try:
            with open(
                    self._PATH + self._FILENAME.format(f"substitutions_{utils.get_callback_date(date)}"),
                    "rb",
            ) as file:
                data = json.loads(file.read())

                return [schedule_parser.models.Substitution(**model) for model in data]
        except Exception:
            return []

    def update_substitutions(
            self,
            date: datetime.datetime,
            substitutions: list[schedule_parser.models.Substitution],
    ) -> None:
        os.makedirs(
            name=self._PATH,
            exist_ok=True,
        )

        with open(
                self._PATH + self._FILENAME.format(f"substitutions_{utils.get_callback_date(date)}"),
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                [model.model_dump() for model in substitutions],
                fp=file,
                ensure_ascii=False,
                indent=2,
            )


class DatabaseManager(pyquoks.data.DatabaseManager):
    class UsersDatabase(pyquoks.data.DatabaseManager.Database):
        _NAME = "users"

        _SQL = textwrap.dedent(
            f"""\
            CREATE TABLE IF NOT EXISTS {_NAME} (
            id INTEGER PRIMARY KEY NOT NULL,
            `group` TEXT NOT NULL,
            is_notifiable BOOLEAN NOT NULL
            )
            """,
        )

        def add_user(self, user: models.User) -> None:
            cursor = self.cursor()

            cursor.execute(
                textwrap.dedent(
                    f"""\
                    INSERT OR IGNORE INTO {self._NAME} (
                    id,
                    `group`,
                    is_notifiable
                    )
                    VALUES (?, ?, ?)
                    """,
                ),
                (
                    user.id,
                    user.group,
                    user.is_notifiable,
                ),
            )

            self.commit()

        def get_user(self, user_id: int) -> models.User | None:
            cursor = self.cursor()

            cursor.execute(
                textwrap.dedent(
                    f"""\
                    SELECT * FROM {self._NAME} WHERE id = ?
                    """,
                ),
                (
                    user_id,
                ),
            )
            result = cursor.fetchone()

            if result:
                return models.User(**dict(result))
            else:
                return None

        def get_users(self) -> list[models.User]:
            cursor = self.cursor()

            cursor.execute(
                textwrap.dedent(
                    f"""\
                    SELECT * FROM {self._NAME}
                    """,
                ),
            )
            results = cursor.fetchall()

            return [models.User(**dict(result)) for result in results]

        def edit_group(self, user_id: int, group: str) -> None:
            cursor = self.cursor()

            cursor.execute(
                textwrap.dedent(
                    f"""\
                    UPDATE {self._NAME} SET `group` = ? WHERE id = ?
                    """,
                ),
                (
                    group,
                    user_id,
                ),
            )

            self.commit()

        def edit_is_notifiable(self, user_id: int, is_notifiable: bool) -> None:
            cursor = self.cursor()

            cursor.execute(
                textwrap.dedent(
                    f"""\
                    UPDATE {self._NAME} SET is_notifiable = ? WHERE id = ?
                    """,
                ),
                (
                    is_notifiable,
                    user_id,
                ),
            )

            self.commit()

        def _edit_setting(self, user_id: int, setting: str, value: bool) -> None:
            edit_callable = getattr(self, f"edit_{setting}", None)

            if edit_callable is None:
                raise AttributeError(
                    name=setting,
                    obj=self,
                )
            else:
                return edit_callable(
                    user_id,
                    value,
                )

    users: UsersDatabase


# endregion

# region Services

class LoggerService(pyquoks.data.LoggerService):
    def log_user_interaction(self, user: aiogram.types.User, interaction: str) -> None:
        user_info = " ".join([
            " | ".join(i for i in [
                user.full_name,
                f"@{user.username}" if user.username else "",
            ] if i),
            f"({user.id})",
        ])
        self.info(f"{user_info} - \"{interaction}\"")

# endregion
