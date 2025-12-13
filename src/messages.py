import aiogram
import aiogram.filters
import aiogram.fsm.context
import openpyxl
import schedule_parser

import constants
import data


class MessagesRouter(aiogram.Router):
    def __init__(
            self,
            strings_provider: data.StringsProvider,
            keyboards_provider: data.KeyboardsProvider,
            config_manager: data.ConfigManager,
            data_manager: data.DataManager,
            logger_service: data.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._strings = strings_provider
        self._keyboards = keyboards_provider
        self._config = config_manager
        self._data = data_manager
        self._logger = logger_service
        self._bot = bot

        super().__init__(
            name=self.__class__.__name__,
        )

        self.message.register(
            self.upload_schedule_handler,
            aiogram.filters.StateFilter(data.States.upload_schedule),
        )
        self.message.register(
            self.upload_substitutions_handler,
            aiogram.filters.StateFilter(data.States.upload_substitutions),
        )

        self._logger.info(f"{self.name} initialized!")

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
                except Exception as e:
                    if type(e) not in constants.IGNORED_EXCEPTIONS:
                        self._logger.log_error(e)

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
                except Exception as e:
                    if type(e) not in constants.IGNORED_EXCEPTIONS:
                        self._logger.log_error(e)

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
