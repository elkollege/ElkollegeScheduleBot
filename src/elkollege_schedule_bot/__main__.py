import asyncio
import logging

import elkollege_schedule_bot.dispatcher
import elkollege_schedule_bot.managers
import elkollege_schedule_bot.providers
import elkollege_schedule_bot.services


async def main() -> None:
    config_manager = elkollege_schedule_bot.managers.config.ConfigManager()
    data_manager = elkollege_schedule_bot.managers.data.DataManager()
    database_manager = elkollege_schedule_bot.managers.database.DatabaseManager()
    environment_provider = elkollege_schedule_bot.providers.environment.EnvironmentProvider()
    strings_provider = elkollege_schedule_bot.providers.strings.StringsProvider()
    buttons_provider = elkollege_schedule_bot.providers.buttons.ButtonsProvider(
        strings_provider=strings_provider,
    )
    keyboards_provider = elkollege_schedule_bot.providers.keyboards.KeyboardsProvider(
        buttons_provider=buttons_provider,
    )

    aiogram_dispatcher = elkollege_schedule_bot.dispatcher.AiogramDispatcher(
        config_manager=config_manager,
        data_manager=data_manager,
        database_manager=database_manager,
        environment_provider=environment_provider,
        keyboards_provider=keyboards_provider,
        strings_provider=strings_provider,
        logger_service=elkollege_schedule_bot.services.logger.LoggerService(
            filename=elkollege_schedule_bot.dispatcher.__name__,
            file_handling=config_manager.settings.file_logging,
            level=logging.INFO,
        ),
    )
    await aiogram_dispatcher.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
