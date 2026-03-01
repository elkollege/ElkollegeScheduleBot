import asyncio
import logging

from . import dispatcher
from .managers import config
from .managers import data
from .managers import database
from .providers import buttons
from .providers import environment
from .providers import keyboards
from .providers import strings
from .services import logger


async def main() -> None:
    config_manager = config.ConfigManager()
    data_manager = data.DataManager()
    database_manager = database.DatabaseManager()
    environment_provider = environment.EnvironmentProvider()
    strings_provider = strings.StringsProvider()
    buttons_provider = buttons.ButtonsProvider(
        strings_provider=strings_provider,
    )
    keyboards_provider = keyboards.KeyboardsProvider(
        buttons_provider=buttons_provider,
    )
    aiogram_dispatcher_logger = logger.LoggerService(
        filename=dispatcher.__name__,
        file_handling=config_manager.settings.file_logging,
        level=logging.INFO,
    )
    aiogram_dispatcher = dispatcher.AiogramDispatcher(
        config_manager=config_manager,
        data_manager=data_manager,
        database_manager=database_manager,
        environment_provider=environment_provider,
        keyboards_provider=keyboards_provider,
        strings_provider=strings_provider,
        logger_service=aiogram_dispatcher_logger,
    )

    await aiogram_dispatcher.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
