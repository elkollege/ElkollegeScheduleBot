import datetime
import json

import aiogram
import aiogram.filters
import aiogram.fsm.context
import openpyxl
import schedule_parser.utils

from .. import constants
from .. import models
from .. import states
from .. import utils
from ..managers import config
from ..managers import database
from ..providers import keyboards
from ..providers import strings
from ..services import logger


class MessagesRouter(aiogram.Router):
    def __init__(
            self,
            config_manager: config.ConfigManager,
            database_manager: database.DatabaseManager,
            keyboards_provider: keyboards.KeyboardsProvider,
            strings_provider: strings.StringsProvider,
            logger_service: logger.LoggerService,
            aiogram_bot: aiogram.Bot,
    ) -> None:
        self._config = config_manager
        self._database = database_manager
        self._keyboards = keyboards_provider
        self._strings = strings_provider
        self._logger = logger_service
        self._bot = aiogram_bot

        super().__init__(
            name=self.__class__.__name__,
        )

        self.message.register(
            self._upload_schedule_handler,
            aiogram.filters.StateFilter(states.upload_schedule),
        )
        self.message.register(
            self._upload_substitutions_handler,
            aiogram.filters.StateFilter(states.upload_substitutions),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Helpers

    def _users_filter(
            self,
            user: models.DatabaseUser,
            /,
            *,
            is_notifiable: bool = None,
            has_group: bool = None,
            is_admin: bool = None,
    ) -> bool:
        self._logger.info(f"{self._users_filter.__name__} ({user=}, {is_notifiable=}, {has_group=}, {is_admin=})")

        if (is_notifiable is not None) and not (is_notifiable == user.is_notifiable):
            return False

        if (has_group is not None) and not (has_group == bool(user.group_name)):
            return False

        if (is_admin is not None) and not (is_admin == (user.id in self._config.settings.admins_list)):
            return False

        return True

    async def _send_notifications(
            self,
            users_list: list[models.DatabaseUser],
            text: str,
            reply_markup: aiogram.types.InlineKeyboardMarkup,
    ) -> None:
        self._logger.info(self._send_notifications.__name__)

        for user in users_list:
            try:
                await self._bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup,
                )
            except Exception as exception:
                if type(exception) not in constants.IGNORED_EXCEPTIONS:
                    self._logger.log_exception(exception)

    async def _send_schedule_uploaded_notifications(self) -> None:
        self._logger.info(self._send_schedule_uploaded_notifications.__name__)

        current_users_list = self._database.users.get_users_list()

        await self._send_notifications(
            users_list=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=True,
                        is_admin=False,
                    ),
                    current_users_list,
                )
            ),
            text=self._strings.menu.notification_schedule_uploaded(),
            reply_markup=self._keyboards.notification_schedule_uploaded(),
        )

    async def _send_substitutions_uploaded_notifications(self, date: datetime.datetime) -> None:
        self._logger.info(f"{self._send_substitutions_uploaded_notifications.__name__} ({date=})")

        current_users_list = self._database.users.get_users_list()

        await self._send_notifications(
            users_list=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=True,
                        is_admin=False,
                    ),
                    current_users_list,
                )
            ),
            text=self._strings.menu.notification_substitutions_uploaded(date),
            reply_markup=self._keyboards.notification_substitutions_uploaded(date),
        )

    # endregion

    # region Handlers

    async def _upload_schedule_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        has_file = bool(message.document)

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self._upload_schedule_handler.__name__} ({has_file=})",
        )

        if has_file:
            with await self._bot.download_file(
                    file_path=(
                            await self._bot.get_file(
                                file_id=message.document.file_id,
                            )
                    ).file_path
            ) as file:
                try:
                    workbook = openpyxl.load_workbook(file)

                    parsed_groups_list = list(
                        schedule_parser.utils.parse_schedule(
                            worksheet=workbook.worksheets[0],
                        )
                    )

                    current_json_string = json.dumps([group.model_dump() for group in parsed_groups_list])

                    current_schedule = self._database.schedules.get_schedule()

                    if current_schedule:
                        self._database.schedules.edit_json_string(
                            json_string=current_json_string,
                        )
                    else:
                        self._database.schedules.add_schedule(
                            json_string=current_json_string,
                        )

                    current_schedule = self._database.schedules.get_schedule()

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_schedule_success(
                            schedule=current_schedule.groups_list,
                        ),
                        reply_markup=self._keyboards.upload_schedule_completed(),
                    )

                    await self._send_schedule_uploaded_notifications()
                except Exception as exception:
                    if type(exception) not in constants.IGNORED_EXCEPTIONS:
                        self._logger.log_exception(exception)

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_schedule_error(),
                        reply_markup=self._keyboards.upload_schedule_completed(),
                    )
                finally:
                    await state.clear()
        else:
            await self._bot.send_message(
                chat_id=message.chat.id,
                text=self._strings.menu.upload_schedule(
                    workbook_extension=self._config.settings.workbook_extension,
                ),
                reply_markup=self._keyboards.upload_schedule(),
            )

    async def _upload_substitutions_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        has_file = bool(message.document)
        current_date = (await state.get_data())["current_date"]

        current_timestamp = utils.get_timestamp_from_date(current_date)

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self._upload_substitutions_handler.__name__} ({has_file=}, {current_date=})",
        )

        if has_file:
            with await self._bot.download_file(
                    file_path=(
                            await self._bot.get_file(
                                file_id=message.document.file_id,
                            )
                    ).file_path
            ) as file:
                try:
                    workbook = openpyxl.load_workbook(file)

                    parsed_substitutions_list = list(
                        schedule_parser.utils.parse_substitutions(
                            worksheet=workbook.worksheets[0],
                        )
                    )

                    current_json_string = json.dumps([substitution.model_dump() for substitution in parsed_substitutions_list])

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    if current_substitution:
                        self._database.substitutions.edit_json_string(
                            timestamp=current_timestamp,
                            json_string=current_json_string,
                        )
                    else:
                        self._database.substitutions.add_substitution(
                            timestamp=current_timestamp,
                            json_string=current_json_string,
                        )

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_substitutions_success(
                            date=current_date,
                            substitutions=current_substitution.substitutions_list,
                        ),
                        reply_markup=self._keyboards.upload_substitutions_completed(
                            date=current_date,
                        ),
                    )

                    await self._send_substitutions_uploaded_notifications(
                        date=current_date,
                    )
                except Exception as exception:
                    if type(exception) not in constants.IGNORED_EXCEPTIONS:
                        self._logger.log_exception(exception)

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_substitutions_error(),
                        reply_markup=self._keyboards.upload_substitutions_completed(
                            date=current_date,
                        ),
                    )
                finally:
                    await state.clear()
        else:
            await self._bot.send_message(
                chat_id=message.chat.id,
                text=self._strings.menu.upload_substitutions(
                    date=current_date,
                    workbook_extension=self._config.settings.workbook_extension,
                ),
                reply_markup=self._keyboards.upload_substitutions(
                    date=current_date,
                ),
            )

    # endregion
