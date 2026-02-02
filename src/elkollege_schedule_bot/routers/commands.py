import aiogram
import aiogram.filters
import pyquoks

import elkollege_schedule_bot.managers
import elkollege_schedule_bot.models
import elkollege_schedule_bot.providers
import elkollege_schedule_bot.services
import elkollege_schedule_bot.utils


class CommandsRouter(aiogram.Router):
    def __init__(
            self,
            config_manager: elkollege_schedule_bot.managers.config.ConfigManager,
            database_manager: elkollege_schedule_bot.managers.database.DatabaseManager,
            keyboards_provider: elkollege_schedule_bot.providers.keyboards.KeyboardsProvider,
            strings_provider: elkollege_schedule_bot.providers.strings.StringsProvider,
            logger_service: elkollege_schedule_bot.services.logger.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._config = config_manager
        self._database = database_manager
        self._keyboards = keyboards_provider
        self._strings = strings_provider
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

        self._database.users.add_user(
            user=elkollege_schedule_bot.models.User(
                id=message.from_user.id,
                **elkollege_schedule_bot.models.User._default_values(),
            ),
        )

        await self._bot.send_message(
            chat_id=message.chat.id,
            message_thread_id=elkollege_schedule_bot.utils.get_message_thread_id(message),
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
                message_thread_id=elkollege_schedule_bot.utils.get_message_thread_id(message),
                text=self._strings.menu.admin(
                    user=message.from_user,
                    time_started=pyquoks.utils.get_process_created_datetime(),
                ),
                reply_markup=self._keyboards.admin(),
            )

    # endregion
