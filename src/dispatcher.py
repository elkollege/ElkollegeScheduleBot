import aiogram
import aiogram.client.default

import src.callbacks
import src.commands
import src.constants
import src.data
import src.messages


class AiogramDispatcher(aiogram.Dispatcher):
    _COMMANDS = [
        aiogram.types.BotCommand(
            command="/start",
            description="Главное меню",
        ),
    ]

    def __init__(
            self,
            strings_provider: src.data.StringsProvider,
            keyboards_provider: src.data.KeyboardsProvider,
            config_manager: src.data.ConfigManager,
            data_manager: src.data.DataManager,
            logger_service: src.data.LoggerService,
    ) -> None:
        self._strings = strings_provider
        self._keyboards = keyboards_provider
        self._config = config_manager
        self._data = data_manager
        self._logger = logger_service
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
            src.commands.CommandsRouter(
                strings_provider=self._strings,
                keyboards_provider=self._keyboards,
                config_manager=self._config,
                logger_service=self._logger,
                bot=self._bot,
            ),
            src.callbacks.CallbacksRouter(
                strings_provider=self._strings,
                keyboards_provider=self._keyboards,
                config_manager=self._config,
                data_manager=self._data,
                logger_service=self._logger,
                bot=self._bot,
            ),
            src.messages.MessagesRouter(
                strings_provider=self._strings,
                keyboards_provider=self._keyboards,
                config_manager=self._config,
                data_manager=self._data,
                logger_service=self._logger,
                bot=self._bot,
            )
        )

        self._logger.info(f"{self.name} initialized!")

    # region Helpers

    async def polling_coroutine(self) -> None:
        try:
            await self._bot.delete_webhook(
                drop_pending_updates=self._config.settings.skip_updates,
            )

            await self.start_polling(self._bot)
        except Exception as e:
            self._logger.log_error(e)

    # endregion

    # region Handlers

    async def error_handler(self, event: aiogram.types.ErrorEvent) -> None:
        if type(event.exception) not in src.constants.IGNORED_EXCEPTIONS:
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
