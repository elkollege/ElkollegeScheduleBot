import aiogram
import aiogram.filters

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
            aiogram.filters.Command("admin"),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def _start_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> None:
        ...  # TODO

    async def _admin_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> None:
        ...  # TODO

    # endregion
