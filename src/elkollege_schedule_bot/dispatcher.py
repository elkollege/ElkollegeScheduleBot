import aiogram
import aiogram.client.default

import elkollege_schedule_bot.constants
import elkollege_schedule_bot.managers
import elkollege_schedule_bot.providers
import elkollege_schedule_bot.routers
import elkollege_schedule_bot.services


class AiogramDispatcher(aiogram.Dispatcher):
    _COMMANDS = [
        aiogram.types.BotCommand(
            command="/start",
            description="Главное меню",
        ),
    ]

    def __init__(
            self,
            config_manager: elkollege_schedule_bot.managers.config.ConfigManager,
            data_manager: elkollege_schedule_bot.managers.data.DataManager,
            database_manager: elkollege_schedule_bot.managers.database.DatabaseManager,
            environment_provider: elkollege_schedule_bot.providers.environment.EnvironmentProvider,
            keyboards_provider: elkollege_schedule_bot.providers.keyboards.KeyboardsProvider,
            strings_provider: elkollege_schedule_bot.providers.strings.StringsProvider,
            logger_service: elkollege_schedule_bot.services.logger.LoggerService,
    ) -> None:
        self._config = config_manager
        self._data = data_manager
        self._database = database_manager
        self._environment = environment_provider
        self._keyboards = keyboards_provider
        self._strings = strings_provider
        self._logger = logger_service
        self._bot = aiogram.Bot(
            token=self._environment.TELEGRAM_BOT_TOKEN,
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
            elkollege_schedule_bot.routers.commands.CommandsRouter(
                config_manager=self._config,
                database_manager=self._database,
                keyboards_provider=self._keyboards,
                strings_provider=self._strings,
                logger_service=self._logger,
                bot=self._bot,
            ),
            elkollege_schedule_bot.routers.callbacks.CallbacksRouter(
                config_manager=self._config,
                data_manager=self._data,
                database_manager=self._database,
                keyboards_provider=self._keyboards,
                strings_provider=self._strings,
                logger_service=self._logger,
                bot=self._bot,
            ),
            elkollege_schedule_bot.routers.messages.MessagesRouter(
                config_manager=self._config,
                data_manager=self._data,
                database_manager=self._database,
                keyboards_provider=self._keyboards,
                strings_provider=self._strings,
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
        except Exception as exception:
            self._logger.log_error(exception)

    # endregion

    # region Handlers

    async def error_handler(self, event: aiogram.types.ErrorEvent) -> None:
        if type(event.exception) not in elkollege_schedule_bot.constants.IGNORED_EXCEPTIONS:
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
