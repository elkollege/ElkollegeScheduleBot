from __future__ import annotations

import datetime

import aiogram
import aiogram.filters
import pyquoks

import data
import utils


class CommandsRouter(aiogram.Router):
    def __init__(
            self,
            strings: data.StringsProvider,
            keyboards: data.KeyboardProvider,
            config: data.ConfigManager,
            logger: data.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._strings = strings
        self._keyboards = keyboards
        self._config = config
        self._logger = logger
        self._bot = bot

        super().__init__(
            name=self.__class__.__name__,
        )

        self.message.register(
            self.admin_handler,
            aiogram.filters.Command(
                "admin",
            ),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def admin_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> None:
        is_admin = message.from_user.id in self._config.settings.admins_list

        self._logger.log_user_interaction(message.from_user, f"{command.text} ({is_admin=})")

        if is_admin:
            await self._bot.send_message(
                chat_id=message.chat.id,
                message_thread_id=utils.get_message_thread_id(message),
                text=self._strings.menu.admin(
                    bot_full_name=(await self._bot.me()).full_name,
                    time_started=pyquoks.utils.get_process_created_datetime().astimezone(
                        tz=datetime.UTC,
                    ),
                ),
                reply_markup=self._keyboards.admin,
            )

    # endregion
