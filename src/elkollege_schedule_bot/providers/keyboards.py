import datetime
import itertools
import math

import aiogram
import aiogram.utils.keyboard
import schedule_parser.models

from . import buttons
from .. import constants
from .. import models


class KeyboardsProvider:
    def __init__(self, buttons_provider: buttons.ButtonsProvider) -> None:
        self._buttons = buttons_provider

    # region Helpers

    def _get_page_buttons(
            self,
            callback_data: str,
            current_page: int,
            items_count: int,
            items_per_page: int,
    ) -> tuple[
        aiogram.types.InlineKeyboardButton,
        aiogram.types.InlineKeyboardButton,
        aiogram.types.InlineKeyboardButton,
    ]:
        total_pages = math.ceil(items_count / items_per_page)
        page_previous = current_page - 1
        page_next = current_page + 1

        return (
            self._buttons.page_previous(
                callback_data=f"{callback_data} {page_previous}",
                is_answer_callback=page_previous < constants.FIRST_PAGE,
            ),
            self._buttons.page_index(
                callback_data=f"{callback_data} {constants.FIRST_PAGE}",
                is_answer_callback=current_page == constants.FIRST_PAGE,
                current_page=current_page,
                total_pages=total_pages,
            ),
            self._buttons.page_next(
                callback_data=f"{callback_data} {page_next}",
                is_answer_callback=page_next > total_pages,
            ),
        )

    # endregion

    # region /start

    def start(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.view_schedules(),
        )
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
        markup_builder.row(
            self._buttons.back_to_start(),
        )

        return markup_builder.as_markup()

    def schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.back_to_view_schedules(),
        )

        return markup_builder.as_markup()

    def view_groups(
            self,
            groups: list[schedule_parser.models.GroupSchedule],
            current_page: int,
    ) -> aiogram.types.InlineKeyboardMarkup:
        buttons_index = current_page - 1

        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.group(group.group_name) for group in list(
                    itertools.batched(
                        groups,
                        constants.GROUPS_PER_PAGE,
                    )
                )[buttons_index]
            ],
            width=constants.GROUPS_PER_ROW,
        )
        markup_builder.row(
            *self._get_page_buttons(
                callback_data="view_groups",
                current_page=current_page,
                items_count=len(groups),
                items_per_page=constants.GROUPS_PER_PAGE,
            ),
        )
        markup_builder.row(
            self._buttons.back_to_start(),
        )

        return markup_builder.as_markup()

    def settings(self, user: models.DatabaseUser) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.switchable_setting(
                    name=setting,
                    value=getattr(user, setting),
                ) for setting in user._switchable_values()
            ],
            width=constants.SETTINGS_PER_ROW,
        )
        markup_builder.row(
            self._buttons.back_to_start(),
        )

        return markup_builder.as_markup()

    # endregion

    # region /admin

    def admin(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.manage_schedule(),
            self._buttons.view_substitutions(),
        )
        markup_builder.row(
            self._buttons.export_logs(),
        )

        return markup_builder.as_markup()

    def manage_schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.upload_schedule(),
            self._buttons.delete_schedule(),
        )
        markup_builder.row(
            self._buttons.back_to_admin(),
        )

        return markup_builder.as_markup()

    def upload_schedule(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.cancel_to_manage_schedule(),
        )

        return markup_builder.as_markup()

    def upload_schedule_completed(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.back_to_manage_schedule(),
        )

        return markup_builder.as_markup()

    def view_substitutions(self) -> aiogram.types.InlineKeyboardMarkup:
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
        markup_builder.row(
            self._buttons.back_to_admin(),
        )

        return markup_builder.as_markup()

    def manage_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.upload_substitutions(date),
            self._buttons.delete_substitutions(date),
        )
        markup_builder.row(
            self._buttons.back_to_view_substitutions(),
        )

        return markup_builder.as_markup()

    def upload_substitutions(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.cancel_to_manage_substitutions(date),
        )

        return markup_builder.as_markup()

    def upload_substitutions_completed(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.back_to_manage_substitutions(date),
        )

        return markup_builder.as_markup()

    # endregion

    # region notification_*

    def notification_schedule_uploaded(self) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.view_schedules(),
        )

        return markup_builder.as_markup()

    def notification_substitutions_uploaded(self, date: datetime.datetime) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            self._buttons.view_schedule(date),
        )

        return markup_builder.as_markup()

    # endregion
