import datetime

import aiogram
import pyquoks.providers.strings
import pyquoks.utils
import schedule_parser.models

from .. import constants
from .. import models
from .. import utils


class StringsProvider(pyquoks.providers.strings.StringsProvider):
    alert: AlertStrings
    button: ButtonStrings
    menu: MenuStrings
    settings: SettingsStrings


class AlertStrings(pyquoks.providers.strings.Strings):

    # region /start

    @classmethod
    def group_selected(cls, group_name: str) -> str:
        return f"Выбрана группа \"{group_name}\"!"

    @classmethod
    def group_not_selected(cls) -> str:
        return "Выберите группу для просмотра расписания!"

    @classmethod
    def group_missing_in_schedule(cls) -> str:
        return "Расписание для выбранной группы отсутствует!"

    # endregion

    # region /admin

    @classmethod
    def schedule_missing(cls) -> str:
        return "Расписание отсутствует!"

    @classmethod
    def schedule_deleted(cls) -> str:
        return "Расписание удалено!"

    @classmethod
    def substitutions_missing(cls) -> str:
        return "Замены отсутствует!"

    @classmethod
    def substitutions_deleted(cls) -> str:
        return "Замены удалено!"

    @classmethod
    def logging_disabled(cls) -> str:
        return "Логирование отключено!"

    # endregion

    @classmethod
    def button_unavailable(cls) -> str:
        return "Эта кнопка недоступна!"


class ButtonStrings(pyquoks.providers.strings.Strings):

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
    def switchable_setting(cls, name: str, value: bool) -> str:
        return f"{name} - {"✅" if value else "❌"}"

    # endregion

    # region /admin

    @classmethod
    def schedule(cls) -> str:
        return "Расписание"

    @classmethod
    def upload(cls) -> str:
        return "Загрузить"

    @classmethod
    def delete(cls) -> str:
        return "Удалить"

    @classmethod
    def substitutions(cls) -> str:
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

    # region page_*

    @classmethod
    def page_previous(cls) -> str:
        return "<"

    @classmethod
    def page_index(cls, current_page: int, total_pages: int) -> str:
        return f"{current_page} / {total_pages}"

    @classmethod
    def page_next(cls) -> str:
        return ">"

    # endregion


class MenuStrings(pyquoks.providers.strings.Strings):

    # region /start

    @classmethod
    def start(cls, user: aiogram.types.User) -> str:
        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Привет, {user.full_name}!</b>
                
                Здесь вы можете просмотреть
                актуальное расписание
                Электростальского колледжа
                для вашей учебной группы.
            """,
        )

    @classmethod
    def view_schedules(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            """
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
        formatted_date = utils.get_readable_date(date)

        readable_schedule = "\n".join(period.readable for period in schedule) if schedule else "ℹ️ Пары отсутствуют"
        substitutions_status = "ℹ️ Замены не загружены" if not has_substitutions else None

        formatted_status = "\n".join(i for i in [
            readable_schedule,
            substitutions_status,
        ] if i)

        return pyquoks.utils.format_multiline_string(
            """
                <b>Расписание на {0}</b>
                
                {1}
            """,
        ).format(formatted_date, formatted_status)

    @classmethod
    def view_groups(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            """
                <b>Выбор группы</b>
                
                Выберите свою учебную
                группу из списка ниже:
            """,
        )

    @classmethod
    def settings(cls, user: models.DatabaseUser) -> str:
        user_id_status = f"User ID: <b>{user.id}</b>"
        group_name_status = f"Группа: <b>{user.group_name}</b>" if user.group_name else None

        formatted_status = "\n".join(i for i in [
            user_id_status,
            group_name_status,
        ] if i)

        return pyquoks.utils.format_multiline_string(
            """
                <b>Настройки</b>
                
                {0}
            """,
        ).format(formatted_status)

    # endregion

    # region /admin

    @classmethod
    def admin(cls, user: aiogram.types.User, date_started: datetime.datetime) -> str:
        formatted_date_started = date_started.astimezone(datetime.UTC).strftime(constants.DATE_FORMAT_STARTED)

        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Меню администратора</b>
                
                Добро пожаловать, {user.full_name}!
                
                Дата запуска: <b>{formatted_date_started} UTC</b>
            """,
        )

    @classmethod
    def manage_schedule(cls, schedule: list[schedule_parser.models.GroupSchedule]) -> str:
        schedule_status = f"Статус расписания: <b>{"Загружено" if schedule else "Отсутствует"}</b>"
        schedule_groups_count_status = f"Учебных групп: <b>{len(schedule)}</b>" if schedule else None

        formatted_status = "\n".join(i for i in [
            schedule_status,
            schedule_groups_count_status,
        ] if i)

        return pyquoks.utils.format_multiline_string(
            """
                <b>Управление расписанием</b>
                
                {0}
            """,
        ).format(formatted_status)

    @classmethod
    def upload_schedule(cls, workbook_extension: str) -> str:
        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Загрузка расписания</b>
                
                Отправьте файл с расширением <b>\".{workbook_extension}\"</b>:
            """,
        )

    @classmethod
    def upload_schedule_error(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Возникла ошибка!</b>
                
                Не удалось обработать расписание.
            """,
        )

    @classmethod
    def upload_schedule_success(cls, schedule: list[schedule_parser.models.GroupSchedule]) -> str:
        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Расписание загружено!</b>
                
                Учебных групп: <b>{len(schedule)}</b>
            """,
        )

    @classmethod
    def view_substitutions(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            """
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
        formatted_date = utils.get_readable_date(date)

        substitutions_status = f"Статус замен: <b>{"Загружены" if substitutions else "Отсутствуют"}</b>"
        substitutions_count_status = f"Замен: <b>{len(substitutions)}</b>" if substitutions else None

        formatted_status = "\n".join(i for i in [
            substitutions_status,
            substitutions_count_status,
        ] if i)

        return pyquoks.utils.format_multiline_string(
            """
                <b>Управление заменами на {0}</b>
                
                {1}
            """,
        ).format(formatted_date, formatted_status)

    @classmethod
    def upload_substitutions(cls, date: datetime.datetime, workbook_extension: str) -> str:
        formatted_date = utils.get_readable_date(date)

        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Загрузка замен на {formatted_date}</b>
                
                Отправьте файл с расширением <b>\".{workbook_extension}\"</b>:
            """,
        )

    @classmethod
    def upload_substitutions_error(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            f"""
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
        formatted_date = utils.get_readable_date(date)

        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Замены на {formatted_date} загружены!</b>
                
                Замен: <b>{len(substitutions)}</b>
            """,
        )

    # endregion

    # region notification_*

    @classmethod
    def notification_schedule_uploaded(cls) -> str:
        return pyquoks.utils.format_multiline_string(
            """
                <b>Загружено новое расписание!</b>
            """,
        )

    @classmethod
    def notification_substitutions_uploaded(cls, date: datetime.datetime) -> str:
        formatted_date = utils.get_readable_date(date)

        return pyquoks.utils.format_multiline_string(
            f"""
                <b>Загружены замены на {formatted_date}!</b>
            """,
        )

    # endregion


class SettingsStrings(pyquoks.providers.strings.Strings):
    @classmethod
    def is_notifiable(cls) -> str:
        return "Уведомления"

    @classmethod
    def _get_setting_string(cls, setting: str) -> str:
        string_callable = getattr(cls, setting, None)

        if string_callable:
            return string_callable()
        else:
            raise AttributeError(
                name=setting,
                obj=cls,
            )
