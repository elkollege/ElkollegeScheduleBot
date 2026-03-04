import datetime

import aiogram

from . import strings
from .. import constants
from .. import utils


class ButtonsProvider:
    def __init__(self, strings_provider: strings.StringsProvider) -> None:
        self._strings = strings_provider

    # region /start

    def view_schedules(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_schedule(),
            callback_data="view_schedules",
        )

    def view_schedule(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_schedule(),
            callback_data=f"schedule {utils.get_timestamp_from_date(date)}",
        )

    @staticmethod
    def schedule(date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=utils.get_readable_date(date),
            callback_data=f"schedule {utils.get_timestamp_from_date(date)}",
        )

    def view_groups(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.view_groups(),
            callback_data=f"view_groups {constants.FIRST_PAGE}",
        )

    @staticmethod
    def group(group_name: str) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=group_name,
            callback_data=f"group {group_name}",
        )

    def settings(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.settings(),
            callback_data="settings",
        )

    def switchable_setting(self, name: str, value: bool) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.switchable_setting(
                name=self._strings.settings._get_setting_string(name),
                value=value,
            ),
            callback_data=f"switchable_setting {name}",
        )

    # endregion

    # region /report

    def contact_developer(self, contact_developer_url: str) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.contact_developer(),
            url=contact_developer_url,
        )

    def source_code(self, source_code_url: str) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.source_code(),
            url=source_code_url,
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
            callback_data=f"manage_substitutions {utils.get_timestamp_from_date(date)}",
        )

    def upload_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.upload(),
            callback_data=f"upload_substitutions {utils.get_timestamp_from_date(date)}",
        )

    def delete_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.delete(),
            callback_data=f"delete_substitutions {utils.get_timestamp_from_date(date)}",
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
            callback_data=f"manage_substitutions {utils.get_timestamp_from_date(date)}",
        )

    def cancel_to_manage_schedule(self) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data="manage_schedule",
        )

    def cancel_to_manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.cancel(),
            callback_data=f"manage_substitutions {utils.get_timestamp_from_date(date)}",
        )

    # endregion

    # region page_*

    def page_previous(
            self,
            callback_data: str,
            is_answer_callback: bool,
    ) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_previous(),
            callback_data="answer_callback" if is_answer_callback else callback_data,
        )

    def page_index(
            self,
            callback_data: str,
            current_page: int,
            total_pages: int,
    ) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_index(
                current_page=current_page,
                total_pages=total_pages,
            ),
            callback_data=f"{callback_data} {total_pages if current_page == constants.FIRST_PAGE else constants.FIRST_PAGE}",
        )

    def page_next(
            self,
            callback_data: str,
            is_answer_callback: bool,
    ) -> aiogram.types.InlineKeyboardButton:
        return aiogram.types.InlineKeyboardButton(
            text=self._strings.button.page_next(),
            callback_data="answer_callback" if is_answer_callback else callback_data,
        )

    # endregion
