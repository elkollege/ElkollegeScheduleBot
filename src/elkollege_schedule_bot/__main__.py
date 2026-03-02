import asyncio
import logging

from .managers import config
from .providers import buttons
from .providers import environment
from .providers import keyboards
from .providers import strings
from .services import logger


async def main() -> None:
    config_manager = config.ConfigManager()
    environment_provider = environment.EnvironmentProvider()
    strings_provider = strings.StringsProvider()
    buttons_provider = buttons.ButtonsProvider(
        strings_provider=strings_provider,
    )
    keyboards_provider = keyboards.KeyboardsProvider(
        buttons_provider=buttons_provider,
    )
    # aiogram_dispatcher_logger = logger.LoggerService(
    #     filename=dispatcher.__name__,
    #     file_handling=config_manager.settings.file_logging,
    #     level=logging.INFO,
    # )


if __name__ == "__main__":
    asyncio.run(main())
