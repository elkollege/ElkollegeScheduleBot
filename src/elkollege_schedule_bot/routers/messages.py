import datetime
import json
import typing

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
            text: typing.Callable[[models.DatabaseUser], str],
            reply_markup: typing.Callable[[models.DatabaseUser], aiogram.types.InlineKeyboardMarkup],
    ) -> None:
        self._logger.info(self._send_notifications.__name__)

        for user in users_list:
            try:
                await self._bot.send_message(
                    chat_id=user.id,
                    text=text(user),
                    reply_markup=reply_markup(user),
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
                        is_admin=False,
                    ),
                    current_users_list,
                )
            ),
            text=lambda _: self._strings.menu.notification_schedule_uploaded(),
            reply_markup=lambda user: self._keyboards.notification_schedule_uploaded(
                has_group=bool(user.group_name),
            ),
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
            text=lambda _: self._strings.menu.notification_substitutions_uploaded(date),
            reply_markup=lambda _: self._keyboards.notification_substitutions_uploaded(date),
        )

    # endregion

    # region Handlers

    async def _upload_schedule_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> typing.Any:
        has_file = bool(message.document)

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self._upload_schedule_handler.__name__} ({has_file=})",
        )

        if not has_file:
            return await self._bot.send_message(
                chat_id=message.chat.id,
                message_thread_id=utils.get_message_thread_id(message),
                text=self._strings.menu.upload_schedule_error(),
                reply_markup=self._keyboards.upload_schedule_completed(),
            )

        with await self._bot.download_file(
                file_path=(
                        await self._bot.get_file(
                            file_id=message.document.file_id,
                        )
                ).file_path
        ) as file:
            try:
                workbook = openpyxl.load_workbook(file)

                current_database_schedule = self._database.schedules.get_schedule()

                parsed_schedule = schedule_parser.utils.parse_schedule(
                    worksheet=workbook.worksheets[0],
                )

                parsed_schedule_json_string = json.dumps(
                    [group_schedule.model_dump() for group_schedule in parsed_schedule]
                )

                if current_database_schedule:
                    self._database.schedules.edit_json_string(
                        json_string=parsed_schedule_json_string,
                    )
                else:
                    self._database.schedules.add_schedule(
                        json_string=parsed_schedule_json_string,
                    )

                current_database_schedule = self._database.schedules.get_schedule()

                await self._bot.send_message(
                    chat_id=message.chat.id,
                    message_thread_id=utils.get_message_thread_id(message),
                    text=self._strings.menu.upload_schedule_success(
                        schedule=current_database_schedule,
                    ),
                    reply_markup=self._keyboards.upload_schedule_completed(),
                )

                await self._send_schedule_uploaded_notifications()
            except Exception as exception:
                if type(exception) not in constants.IGNORED_EXCEPTIONS:
                    self._logger.log_exception(exception)

                await self._bot.send_message(
                    chat_id=message.chat.id,
                    message_thread_id=utils.get_message_thread_id(message),
                    text=self._strings.menu.upload_schedule_error(),
                    reply_markup=self._keyboards.upload_schedule_completed(),
                )
            finally:
                await state.clear()

    async def _upload_substitutions_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> typing.Any:
        current_timestamp = (await state.get_data())["current_timestamp"]
        current_date = utils.get_date_from_timestamp(current_timestamp)
        has_file = bool(message.document)

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self._upload_substitutions_handler.__name__} ({has_file=}, {current_timestamp=})",
        )

        if not has_file:
            return await self._bot.send_message(
                chat_id=message.chat.id,
                message_thread_id=utils.get_message_thread_id(message),
                text=self._strings.menu.upload_substitutions_error(),
                reply_markup=self._keyboards.upload_substitutions_completed(
                    date=current_date,
                ),
            )

        with await self._bot.download_file(
                file_path=(
                        await self._bot.get_file(
                            file_id=message.document.file_id,
                        )
                ).file_path
        ) as file:
            try:
                workbook = openpyxl.load_workbook(file)

                current_database_substitution = self._database.substitutions.get_substitution(
                    timestamp=current_timestamp,
                )

                parsed_substitutions = schedule_parser.utils.parse_substitutions(
                    worksheet=workbook.worksheets[0],
                )

                parsed_substitutions_json_string = json.dumps(
                    [substitution.model_dump() for substitution in parsed_substitutions]
                )

                if current_database_substitution:
                    self._database.substitutions.edit_json_string(
                        timestamp=current_timestamp,
                        json_string=parsed_substitutions_json_string,
                    )
                else:
                    self._database.substitutions.add_substitution(
                        timestamp=current_timestamp,
                        json_string=parsed_substitutions_json_string,
                    )

                current_database_substitution = self._database.substitutions.get_substitution(
                    timestamp=current_timestamp,
                )

                await self._bot.send_message(
                    chat_id=message.chat.id,
                    message_thread_id=utils.get_message_thread_id(message),
                    text=self._strings.menu.upload_substitutions_success(
                        date=current_date,
                        substitution=current_database_substitution,
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
                    message_thread_id=utils.get_message_thread_id(message),
                    text=self._strings.menu.upload_substitutions_error(),
                    reply_markup=self._keyboards.upload_substitutions_completed(
                        date=current_date,
                    ),
                )
            finally:
                await state.clear()

    # endregion
