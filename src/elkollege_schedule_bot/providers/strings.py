import datetime
import textwrap

import aiogram
import pyquoks
import schedule_parser

import elkollege_schedule_bot.models
import elkollege_schedule_bot.utils


class StringsProvider(pyquoks.providers.strings.StringsProvider):
    alert: AlertStrings
    button: ButtonStrings
    menu: MenuStrings
    settings: SettingsStrings


class AlertStrings(pyquoks.providers.strings.Strings):

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


class ButtonStrings(pyquoks.providers.strings.Strings):

    # region /start

    @classmethod
    def view_schedules(cls) -> str:
        return "Просмотр расписания"

    @classmethod
    def schedule_readable(cls, date: datetime.datetime) -> str:
        return f"Расписание на {elkollege_schedule_bot.utils.get_readable_date(date)}"

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


class MenuStrings(pyquoks.providers.strings.Strings):

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
        return f"<b>Расписание на {elkollege_schedule_bot.utils.get_readable_date(date)}</b>{"\n*Замены не загружены*" if not has_substitutions else ""}\n\n{readable_schedule}"

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
    def settings(cls, user: elkollege_schedule_bot.models.User) -> str:
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
            <b>Управление заменами на {elkollege_schedule_bot.utils.get_readable_date(date)}</b>

            Статус замен: <b>{"Загружены" if substitutions else "Отсутствуют"}</b>
            {f"Замен: <b>{len(substitutions)}</b>" if substitutions else ""}
            """,
        )

    @classmethod
    def upload_substitutions(cls, date: datetime.datetime, workbook_extension: str) -> str:
        return textwrap.dedent(
            f"""\
            <b>Загрузка замен на {elkollege_schedule_bot.utils.get_readable_date(date)}</b>

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
            <b>Замены на {elkollege_schedule_bot.utils.get_readable_date(date)} загружены!</b>

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
        return f"Загружены замены на {elkollege_schedule_bot.utils.get_readable_date(date)}!"

    # endregion


class SettingsStrings(pyquoks.providers.strings.Strings):
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
