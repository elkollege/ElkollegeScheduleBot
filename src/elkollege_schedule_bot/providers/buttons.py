import datetime

import aiogram
import schedule_parser

import elkollege_schedule_bot.constants
import elkollege_schedule_bot.providers
import elkollege_schedule_bot.utils


class ButtonsProvider:
    def __init__(self, strings_provider: elkollege_schedule_bot.providers.strings.StringsProvider) -> None:
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
            text=elkollege_schedule_bot.utils.get_readable_date(date),
            callback_data=f"schedule {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    def schedule_readable(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.schedule_readable(date),
            callback_data=f"schedule {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    def view_groups(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_groups(),
            callback_data=f"view_groups {elkollege_schedule_bot.constants.FIRST_PAGE}",
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
            text=elkollege_schedule_bot.utils.get_readable_date(date),
            callback_data=f"manage_substitutions {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    def upload_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.upload(),
            callback_data=f"upload_substitutions {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    def delete_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.delete(),
            callback_data=f"delete_substitutions {elkollege_schedule_bot.utils.get_callback_date(date)}",
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
            callback_data=f"manage_substitutions {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    def cancel_to_manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data="manage_schedule",
        )

    def cancel_to_manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data=f"manage_substitutions {elkollege_schedule_bot.utils.get_callback_date(date)}",
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
            callback_data=f"schedule {elkollege_schedule_bot.utils.get_callback_date(date)}",
        )

    # endregion
