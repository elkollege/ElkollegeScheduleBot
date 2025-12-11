import aiogram
import aiogram.filters
import aiogram.fsm.context
import openpyxl
import schedule_parser

import src.constants
import src.data


class MessagesRouter(aiogram.Router):
    def __init__(
            self,
            strings_provider: src.data.StringsProvider,
            keyboards_provider: src.data.KeyboardsProvider,
            config_manager: src.data.ConfigManager,
            data_manager: src.data.DataManager,
            logger_service: src.data.LoggerService,
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
            aiogram.filters.StateFilter(src.data.States.upload_schedule),
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
                            groups_count=len(self._data.schedule),
                        ),
                        reply_markup=self._keyboards.upload_schedule_ended(),
                    )
                except Exception as e:
                    if type(e) not in src.constants.IGNORED_EXCEPTIONS:
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
                    schedule_extension=self._config.settings.workbook_extension,
                ),
                reply_markup=self._keyboards.upload_schedule(),
            )

    # endregion
