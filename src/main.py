import asyncio
import logging

import data
import dispatcher


async def main() -> None:
    environment_provider = data.EnvironmentProvider()
    strings_provider = data.StringsProvider()
    config_manager = data.ConfigManager()
    data_manager = data.DataManager()
    database_manager = data.DatabaseManager()
    buttons_provider = data.ButtonsProvider(
        strings_provider=strings_provider,
    )
    keyboards_provider = data.KeyboardsProvider(
        buttons_provider=buttons_provider,
    )

    bot = dispatcher.AiogramDispatcher(
        environment_provider=environment_provider,
        strings_provider=strings_provider,
        keyboards_provider=keyboards_provider,
        config_manager=config_manager,
        data_manager=data_manager,
        database_manager=database_manager,
        logger_service=data.LoggerService(
            filename=dispatcher.__name__,
            file_handling=config_manager.settings.file_logging,
            level=logging.INFO,
        ),
    )
    await bot.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
