import aiogram
import aiogram.exceptions
import aiogram.filters
import aiogram.fsm.context
import pyquoks

import src.constants
import src.data
import src.utils


class CallbacksRouter(aiogram.Router):
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

        self.callback_query.register(
            self.callback_handler,
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def callback_handler(
            self,
            call: aiogram.types.CallbackQuery,
            state: aiogram.fsm.context.FSMContext,
    ) -> None:
        is_admin = call.from_user.id in self._config.settings.admins_list

        self._logger.log_user_interaction(
            user=call.from_user,
            interaction=f"{call.data} ({is_admin=})",
        )

        await state.clear()

        try:
            match call.data:
                case _:
                    if is_admin:
                        match call.data:
                            case "admin":
                                await self._bot.edit_message_text(
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=self._strings.menu.admin(
                                        user=call.from_user,
                                        time_started=pyquoks.utils.get_process_created_datetime(),
                                    ),
                                    reply_markup=self._keyboards.admin(),
                                )
                            case "manage_schedule":
                                await self._bot.edit_message_text(
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=self._strings.menu.manage_schedule(
                                        schedule_availability=bool(self._data.schedule)),
                                    reply_markup=self._keyboards.manage_schedule(),
                                )
                            case "upload_schedule":
                                await self._bot.edit_message_text(
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=self._strings.menu.upload_schedule(
                                        schedule_extension=self._config.settings.workbook_extension,
                                    ),
                                    reply_markup=self._keyboards.upload_schedule(),
                                )

                                await state.set_state(src.data.States.upload_schedule)
                            case "delete_schedule":
                                if self._data.schedule:
                                    self._data.update(
                                        schedule=[],
                                    )

                                    await self._bot.edit_message_text(
                                        chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text=self._strings.menu.manage_schedule(
                                            schedule_availability=bool(self._data.schedule)),
                                        reply_markup=self._keyboards.manage_schedule(),
                                    )

                                    await self._bot.answer_callback_query(
                                        callback_query_id=call.id,
                                        text=self._strings.alert.schedule_deleted(),
                                        show_alert=True,
                                    )
                                else:
                                    await self._bot.answer_callback_query(
                                        callback_query_id=call.id,
                                        text=self._strings.alert.schedule_unavailable(),
                                        show_alert=True,
                                    )
                            case "export_logs":
                                if self._config.settings.file_logging:
                                    logs_file = self._logger.file

                                    await self._bot.send_document(
                                        chat_id=call.message.chat.id,
                                        message_thread_id=src.utils.get_message_thread_id(call.message),
                                        document=aiogram.types.BufferedInputFile(
                                            file=logs_file.read(),
                                            filename=logs_file.name,
                                        ),
                                    )

                                    logs_file.close()
                                else:
                                    await self._bot.answer_callback_query(
                                        callback_query_id=call.id,
                                        text=self._strings.alert.export_logs_unavailable(),
                                        show_alert=True,
                                    )
                            case _:
                                await self._bot.answer_callback_query(
                                    callback_query_id=call.id,
                                    text=self._strings.alert.button_unavailable(),
                                    show_alert=True,
                                )
                    else:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.button_unavailable(),
                            show_alert=True,
                        )
        except Exception as e:
            if type(e) not in src.constants.IGNORED_EXCEPTIONS:
                self._logger.log_error(e)
        finally:
            await self._bot.answer_callback_query(
                callback_query_id=call.id,
            )

    # endregion
