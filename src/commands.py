import aiogram
import aiogram.filters
import pyquoks

import data
import utils


class CommandsRouter(aiogram.Router):
    def __init__(
            self,
            strings_provider: data.StringsProvider,
            keyboards_provider: data.KeyboardsProvider,
            config_manager: data.ConfigManager,
            logger_service: data.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._strings = strings_provider
        self._keyboards = keyboards_provider
        self._config = config_manager
        self._logger = logger_service
        self._bot = bot

        super().__init__(
            name=self.__class__.__name__,
        )

        self.message.register(
            self.start_handler,
            aiogram.filters.CommandStart(),
        )
        self.message.register(
            self.admin_handler,
            aiogram.filters.Command("admin"),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def start_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> None:
        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=command.text,
        )

        await self._bot.send_message(
            chat_id=message.chat.id,
            message_thread_id=utils.get_message_thread_id(message),
            text=self._strings.menu.start(
                user=message.from_user,
            ),
            reply_markup=self._keyboards.start(),
        )

    async def admin_handler(
            self,
            message: aiogram.types.Message,
            command: aiogram.filters.CommandObject,
    ) -> None:
        is_admin = message.from_user.id in self._config.settings.admins_list

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{command.text} ({is_admin=})",
        )

        if is_admin:
            await self._bot.send_message(
                chat_id=message.chat.id,
                message_thread_id=utils.get_message_thread_id(message),
                text=self._strings.menu.admin(
                    user=message.from_user,
                    time_started=pyquoks.utils.get_process_created_datetime(),
                ),
                reply_markup=self._keyboards.admin(),
            )

    # endregion
