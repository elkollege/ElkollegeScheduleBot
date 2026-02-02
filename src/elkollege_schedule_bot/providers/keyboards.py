import datetime
import itertools
import math

import aiogram.utils.keyboard
import schedule_parser

import elkollege_schedule_bot.constants
import elkollege_schedule_bot.models
import elkollege_schedule_bot.providers


class KeyboardsProvider:
    def __init__(self, buttons_provider: elkollege_schedule_bot.providers.buttons.ButtonsProvider) -> None:
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
                is_answer_callback=page_previous < elkollege_schedule_bot.constants.FIRST_PAGE,
            ),
            self._buttons.page_info(
                callback=f"{callback} {elkollege_schedule_bot.constants.FIRST_PAGE}",
                is_answer_callback=page == elkollege_schedule_bot.constants.FIRST_PAGE,
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
                ) for days_delta in range(elkollege_schedule_bot.constants.SCHEDULE_DAYS)
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
                        elkollege_schedule_bot.constants.GROUPS_PER_PAGE
                    )
                )[buttons_index]
            ],
            width=elkollege_schedule_bot.constants.GROUPS_PER_ROW,
        )
        markup_builder.row(
            *self._get_page_buttons(
                callback="view_groups",
                page=page,
                items_count=len(groups),
                items_per_page=elkollege_schedule_bot.constants.GROUPS_PER_PAGE,
            ),
        )
        markup_builder.row(self._buttons.back_to_start())

        return markup_builder.as_markup()

    def settings(self, user: elkollege_schedule_bot.models.User) -> aiogram.types.InlineKeyboardMarkup:
        markup_builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
        markup_builder.row(
            *[
                self._buttons.settings_switch(
                    name=setting,
                    value=getattr(user, setting)
                ) for setting in user._switchable_values()
            ],
            width=elkollege_schedule_bot.constants.SETTINGS_PER_ROW,
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
                ) for days_delta in range(elkollege_schedule_bot.constants.SCHEDULE_DAYS)
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
        markup_builder.row(self._buttons.schedule_readable(date))

        return markup_builder.as_markup()

    # endregion
