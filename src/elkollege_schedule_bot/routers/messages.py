import datetime

import aiogram
import aiogram.filters
import aiogram.fsm.context

from .. import constants
from .. import models
from .. import states
from ..managers import config
from ..managers import database
from ..providers import keyboards
from ..providers import strings
from ..services import logger


class MessagesRouter(aiogram.Router):
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
            self._upload_schedule_handler,
            aiogram.filters.StateFilter(states.upload_schedule),
        )
        self.message.register(
            self._upload_substitutions_handler,
            aiogram.filters.StateFilter(states.upload_substitutions),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Helpers

    def _users_filter(
            self,
            user: models.DatabaseUser,
            /,
            *,
            is_notifiable: bool = None,
            has_group: bool = None,
            is_admin: bool = None,
    ) -> bool:
        self._logger.info(f"{self._users_filter.__name__} ({user=}, {is_notifiable=}, {has_group=}, {is_admin=})")

        if (is_notifiable is not None) and not (is_notifiable == user.is_notifiable):
            return False

        if (has_group is not None) and not (has_group == bool(user.group_name)):
            return False

        if (is_admin is not None) and not (is_admin == (user.id in self._config.settings.admins_list)):
            return False

        return True

    async def _send_notifications(
            self,
            users_list: list[models.DatabaseUser],
            text: str,
            reply_markup: aiogram.types.InlineKeyboardMarkup,
    ) -> None:
        self._logger.info(self._send_notifications.__name__)

        for user in users_list:
            try:
                await self._bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup,
                )
            except Exception as exception:
                if type(exception) not in constants.IGNORED_EXCEPTIONS:
                    self._logger.log_exception(exception)

    async def _send_schedule_uploaded_notifications(self) -> None:
        self._logger.info(self._send_schedule_uploaded_notifications.__name__)

        current_users_list = self._database.users.get_users_list()

        await self._send_notifications(
            users_list=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=False,
                        is_admin=False,
                    ),
                    current_users_list,
                )
            ),
            text=self._strings.menu.notification_schedule_uploaded(),
            reply_markup=self._keyboards.notification_schedule_uploaded(),
        )

    async def _send_substitutions_uploaded_notifications(self, date: datetime.datetime) -> None:
        self._logger.info(f"{self._send_substitutions_uploaded_notifications.__name__} ({date=})")

        current_users_list = self._database.users.get_users_list()

        await self._send_notifications(
            users_list=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=True,
                        is_admin=False,
                    ),
                    current_users_list,
                )
            ),
            text=self._strings.menu.notification_substitutions_uploaded(date),
            reply_markup=self._keyboards.notification_substitutions_uploaded(date),
        )

    # endregion

    # region Handlers

    async def _upload_schedule_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        ...  # TODO

    async def _upload_substitutions_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        ...  # TODO

    # endregion
