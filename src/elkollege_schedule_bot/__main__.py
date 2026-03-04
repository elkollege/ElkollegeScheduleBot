import asyncio
import logging

import aiogram
import aiogram.client.default

from . import dispatcher
from .managers import config
from .managers import database
from .providers import buttons
from .providers import environment
from .providers import keyboards
from .providers import strings
from .services import logger


async def main() -> None:
    config_manager = config.ConfigManager()
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
    aiogram_bot = aiogram.Bot(
        token=environment_provider.TELEGRAM_BOT_TOKEN,
        default=aiogram.client.default.DefaultBotProperties(
            parse_mode=aiogram.enums.ParseMode.HTML,
        ),
    )
    aiogram_dispatcher = dispatcher.AiogramDispatcher(
        config_manager=config_manager,
        database_manager=database_manager,
        keyboards_provider=keyboards_provider,
        strings_provider=strings_provider,
        logger_service=aiogram_dispatcher_logger,
        aiogram_bot=aiogram_bot,
    )

    await aiogram_dispatcher.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
