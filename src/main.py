import asyncio
import logging

import src.data
import src.dispatcher


async def main() -> None:
    strings_provider = src.data.StringsProvider()
    config_manager = src.data.ConfigManager()
    data_manager = src.data.DataManager()
    buttons_provider = src.data.ButtonsProvider(
        strings_provider=strings_provider,
    )
    keyboards_provider = src.data.KeyboardsProvider(
        buttons_provider=buttons_provider,
    )

    bot = src.dispatcher.AiogramDispatcher(
        strings_provider=strings_provider,
        keyboards_provider=keyboards_provider,
        config_manager=config_manager,
        data_manager=data_manager,
        logger_service=src.data.LoggerService(
            filename=src.dispatcher.__name__,
            file_handling=config_manager.settings.file_logging,
            level=logging.INFO,
        )
    )
    await bot.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
