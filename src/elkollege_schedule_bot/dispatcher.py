import aiogram

from . import constants
from .managers import config
from .managers import database
from .providers import keyboards
from .providers import strings
from .routers import callbacks
from .routers import commands
from .services import logger


class AiogramDispatcher(aiogram.Dispatcher):
    _COMMANDS = [
        aiogram.types.BotCommand(
            command="/start",
            description="Главное меню",
        ),
    ]

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

        self.startup.register(
            self._startup_handler,
        )

        self.errors.register(
            self._error_handler,
        )

        self.shutdown.register(
            self._shutdown_handler,
        )

        self.include_routers(
            callbacks.CallbacksRouter(
                config_manager=config_manager,
                database_manager=database_manager,
                keyboards_provider=keyboards_provider,
                strings_provider=strings_provider,
                logger_service=logger_service,
                aiogram_bot=aiogram_bot,
            ),
            commands.CommandsRouter(
                config_manager=config_manager,
                database_manager=database_manager,
                keyboards_provider=keyboards_provider,
                strings_provider=strings_provider,
                logger_service=logger_service,
                aiogram_bot=aiogram_bot,
            ),
            # TODO: messages
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
            self._logger.log_exception(exception)

    # endregion

    # region Handlers

    async def _startup_handler(self) -> None:
        await self._bot.set_my_commands(
            commands=self._COMMANDS,
            scope=aiogram.types.BotCommandScopeDefault(),
        )

        self._logger.info(f"{self.name} started!")

    async def _error_handler(self, event: aiogram.types.ErrorEvent) -> None:
        if type(event.exception) not in constants.IGNORED_EXCEPTIONS:
            self._logger.log_exception(event.exception)

    async def _shutdown_handler(self) -> None:
        self._logger.info(f"{self.name} terminated")

    # endregion
