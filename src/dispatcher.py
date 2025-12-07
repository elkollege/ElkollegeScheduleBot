from __future__ import annotations

import aiogram
import aiogram.client.default
import aiogram.exceptions

import callbacks
import commands
import data


class AiogramDispatcher(aiogram.Dispatcher):
    _COMMANDS = [
        aiogram.types.BotCommand(
            command="/start",
            description="Главное меню",
        ),
    ]

    _IGNORED_EXCEPTIONS = [
        aiogram.exceptions.TelegramForbiddenError,
        aiogram.exceptions.TelegramRetryAfter,
    ]

    def __init__(
            self,
            strings: data.StringsProvider,
            keyboards: data.KeyboardProvider,
            config: data.ConfigManager,
            logger: data.LoggerService,
    ) -> None:
        self._strings = strings
        self._keyboards = keyboards
        self._config = config
        self._logger = logger
        self._bot = aiogram.Bot(
            token=self._config.settings.bot_token,
            default=aiogram.client.default.DefaultBotProperties(
                parse_mode=aiogram.enums.ParseMode.HTML,
            ),
        )

        super().__init__(
            name=self.__class__.__name__,
        )

        self.errors.register(
            self.error_handler,
        )
        self.startup.register(
            self.startup_handler,
        )
        self.shutdown.register(
            self.shutdown_handler,
        )

        self.include_routers(
            commands.CommandsRouter(
                strings=self._strings,
                keyboards=self._keyboards,
                config=self._config,
                logger=self._logger,
                bot=self._bot,
            ),
            callbacks.CallbacksRouter(
                strings=self._strings,
                config=self._config,
                logger=self._logger,
                bot=self._bot,
            ),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Helpers

    async def polling_coroutine(self) -> None:
        try:
            await self._bot.delete_webhook(
                drop_pending_updates=self._config.settings.skip_updates,
            )

            await self.start_polling(self._bot)
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
            )

    # endregion

    # region Handlers

    async def error_handler(self, event: aiogram.types.ErrorEvent) -> None:
        if type(event.exception) not in self._IGNORED_EXCEPTIONS:
            self._logger.log_error(
                exception=event.exception,
            )

    async def startup_handler(self) -> None:
        await self._bot.set_my_commands(
            commands=self._COMMANDS,
            scope=aiogram.types.BotCommandScopeDefault(),
        )

        self._logger.info(f"{self.name} started!")

    async def shutdown_handler(self) -> None:
        self._logger.info(f"{self.name} terminated")

    # endregion
