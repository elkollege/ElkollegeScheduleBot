import asyncio
import logging

import data
import dispatcher


async def main() -> None:
    strings = data.StringsProvider()
    config = data.ConfigManager()
    buttons = data.ButtonsProvider(
        strings=strings,
    )
    keyboards = data.KeyboardProvider(
        buttons=buttons,
    )

    bot = dispatcher.AiogramDispatcher(
        strings=strings,
        keyboards=keyboards,
        config=config,
        logger=data.LoggerService(
            filename=dispatcher.__name__,
            file_handling=config.settings.file_logging,
            level=logging.INFO,
        )
    )
    await bot.polling_coroutine()


if __name__ == "__main__":
    asyncio.run(main())
