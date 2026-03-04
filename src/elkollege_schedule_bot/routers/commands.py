import typing

import aiogram
import aiogram.filters
import pyquoks.utils

from .. import models
from .. import utils
from ..managers import config
from ..managers import database
from ..providers import keyboards
from ..providers import strings
from ..services import logger


class CommandsRouter(aiogram.Router):
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
            self._start_handler,
            aiogram.filters.CommandStart(),
        )

        self.message.register(
            self._admin_handler,
            aiogram.filters.Command("admin", "adm"),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def _start_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> typing.Any:
        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=command.text,
        )

        self._database.users.add_user(
            _id=message.from_user.id,
            **models.DatabaseUser._default_values(),
        )

        await self._bot.send_message(
            chat_id=message.chat.id,
            message_thread_id=utils.get_message_thread_id(message),
            text=self._strings.menu.start(
                user=message.from_user,
            ),
            reply_markup=self._keyboards.start(),
        )

    async def _admin_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> typing.Any:
        is_admin = message.from_user.id in self._config.settings.admins_list

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{command.text} ({is_admin=})",
        )

        if not is_admin:
            return

        await self._bot.send_message(
            chat_id=message.chat.id,
            message_thread_id=utils.get_message_thread_id(message),
            text=self._strings.menu.admin(
                user=message.from_user,
                date_started=pyquoks.utils.get_process_created_datetime(),
            ),
            reply_markup=self._keyboards.admin(),
        )

    # endregion
