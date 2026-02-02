import datetime

import aiogram
import aiogram.filters
import aiogram.fsm.context
import openpyxl
import schedule_parser

import elkollege_schedule_bot.constants
import elkollege_schedule_bot.managers
import elkollege_schedule_bot.models
import elkollege_schedule_bot.providers
import elkollege_schedule_bot.services
import elkollege_schedule_bot.states


class MessagesRouter(aiogram.Router):
    def __init__(
            self,
            config_manager: elkollege_schedule_bot.managers.config.ConfigManager,
            data_manager: elkollege_schedule_bot.managers.data.DataManager,
            database_manager: elkollege_schedule_bot.managers.database.DatabaseManager,
            keyboards_provider: elkollege_schedule_bot.providers.keyboards.KeyboardsProvider,
            strings_provider: elkollege_schedule_bot.providers.strings.StringsProvider,
            logger_service: elkollege_schedule_bot.services.logger.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._config = config_manager
        self._data = data_manager
        self._database = database_manager
        self._keyboards = keyboards_provider
        self._strings = strings_provider
        self._logger = logger_service
        self._bot = bot

        super().__init__(
            name=self.__class__.__name__,
        )

        self.message.register(
            self.upload_schedule_handler,
            aiogram.filters.StateFilter(elkollege_schedule_bot.states.States.upload_schedule),
        )
        self.message.register(
            self.upload_substitutions_handler,
            aiogram.filters.StateFilter(elkollege_schedule_bot.states.States.upload_substitutions),
        )

        self._logger.info(f"{self.name} initialized!")

    # region Helpers

    def _users_filter(
            self,
            user: elkollege_schedule_bot.models.User,
            /,
            *,
            is_notifiable: bool = None,
            has_group: bool = None,
            is_admin: bool = None,
    ) -> bool:
        self._logger.info(
            msg=f"{self._users_filter.__name__} ({user=}, {is_notifiable=}, {has_group=}, {is_admin=})",
        )

        if (is_notifiable is not None) and not (is_notifiable == user.is_notifiable):
            return False

        if (has_group is not None) and not (has_group == bool(user.group)):
            return False

        if (is_admin is not None) and not (is_admin == (user.id in self._config.settings.admins_list)):
            return False

        return True

    async def _send_notifications(
            self,
            users: list[elkollege_schedule_bot.models.User],
            text: str,
            reply_markup: aiogram.types.InlineKeyboardMarkup,
    ) -> None:
        self._logger.info(
            msg=self._send_notifications.__name__,
        )

        for user in users:
            try:
                await self._bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup,
                )
            except Exception as exception:
                if type(exception) not in elkollege_schedule_bot.constants.IGNORED_EXCEPTIONS:
                    self._logger.log_error(exception)

    async def _send_schedule_uploaded_notifications(self) -> None:
        self._logger.info(
            msg=self._send_schedule_uploaded_notifications.__name__,
        )

        await self._send_notifications(
            users=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=True,
                        is_admin=False,
                    ),
                    self._database.users.get_users(),
                )
            ),
            text=self._strings.menu.notification_schedule_uploaded(),
            reply_markup=self._keyboards.notification_schedule_uploaded(),
        )

    async def _send_substitutions_uploaded_notifications(self, date: datetime.datetime) -> None:
        self._logger.info(
            msg=f"{self._send_substitutions_uploaded_notifications.__name__} ({date=})",
        )

        await self._send_notifications(
            users=list(
                filter(
                    lambda user: self._users_filter(
                        user,
                        is_notifiable=True,
                        has_group=True,
                        is_admin=False,
                    ),
                    self._database.users.get_users(),
                )
            ),
            text=self._strings.menu.notification_substitutions_uploaded(date),
            reply_markup=self._keyboards.notification_substitutions_uploaded(date),
        )

    # endregion

    # region Handlers

    async def upload_schedule_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        has_file = bool(message.document)

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self.upload_schedule_handler.__name__} ({has_file=})",
        )

        if has_file:
            with await self._bot.download_file(
                    file_path=(
                            await self._bot.get_file(
                                file_id=message.document.file_id,
                            )
                    ).file_path,
            ) as file:
                try:
                    workbook = openpyxl.load_workbook(file)

                    self._data.update(
                        schedule=list(
                            schedule_parser.utils.parse_schedule(
                                worksheet=workbook.worksheets[0],
                            )
                        ),
                    )

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_schedule_success(
                            schedule=self._data.schedule,
                        ),
                        reply_markup=self._keyboards.upload_schedule_ended(),
                    )

                    await self._send_schedule_uploaded_notifications()
                except Exception as exception:
                    if type(exception) not in elkollege_schedule_bot.constants.IGNORED_EXCEPTIONS:
                        self._logger.log_error(exception)

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_schedule_error(),
                        reply_markup=self._keyboards.upload_schedule_ended(),
                    )
                finally:
                    await state.clear()
        else:
            await self._bot.send_message(
                chat_id=message.chat.id,
                text=self._strings.menu.upload_schedule(
                    workbook_extension=self._config.settings.workbook_extension,
                ),
                reply_markup=self._keyboards.upload_schedule(),
            )

    async def upload_substitutions_handler(
            self,
            message: aiogram.types.Message,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        has_file = bool(message.document)

        current_date = (await state.get_data())["current_date"]

        self._logger.log_user_interaction(
            user=message.from_user,
            interaction=f"{self.upload_substitutions_handler.__name__} ({current_date=}, {has_file=})",
        )

        if has_file:
            with await self._bot.download_file(
                    file_path=(
                            await self._bot.get_file(
                                file_id=message.document.file_id,
                            )
                    ).file_path,
            ) as file:
                try:
                    workbook = openpyxl.load_workbook(file)

                    self._data.update_substitutions(
                        date=current_date,
                        substitutions=list(
                            schedule_parser.utils.parse_substitutions(
                                worksheet=workbook.worksheets[0],
                            )
                        ),
                    )

                    current_substitutions = self._data.get_substitutions(current_date)

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_substitutions_success(
                            date=current_date,
                            substitutions=current_substitutions,
                        ),
                        reply_markup=self._keyboards.upload_substitutions_ended(
                            date=current_date,
                        ),
                    )

                    await self._send_substitutions_uploaded_notifications(
                        date=current_date,
                    )
                except Exception as exception:
                    if type(exception) not in elkollege_schedule_bot.constants.IGNORED_EXCEPTIONS:
                        self._logger.log_error(exception)

                    await self._bot.send_message(
                        chat_id=message.chat.id,
                        text=self._strings.menu.upload_substitutions_error(),
                        reply_markup=self._keyboards.upload_substitutions_ended(
                            date=current_date,
                        ),
                    )
                finally:
                    await state.clear()
        else:
            await self._bot.send_message(
                chat_id=message.chat.id,
                text=self._strings.menu.upload_substitutions(
                    date=current_date,
                    workbook_extension=self._config.settings.workbook_extension,
                ),
                reply_markup=self._keyboards.upload_substitutions(
                    date=current_date,
                ),
            )

    # endregion
