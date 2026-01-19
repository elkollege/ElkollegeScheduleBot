import aiogram
import aiogram.exceptions
import aiogram.filters
import aiogram.fsm.context
import pyquoks
import schedule_parser

import constants
import data
import models
import utils


class CallbacksRouter(aiogram.Router):
    def __init__(
            self,
            strings_provider: data.StringsProvider,
            keyboards_provider: data.KeyboardsProvider,
            config_manager: data.ConfigManager,
            data_manager: data.DataManager,
            database_manager: data.DatabaseManager,
            logger_service: data.LoggerService,
            bot: aiogram.Bot,
    ) -> None:
        self._strings = strings_provider
        self._keyboards = keyboards_provider
        self._config = config_manager
        self._data = data_manager
        self._database = database_manager
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

        self._database.users.add_user(
            user=models.User(
                id=call.from_user.id,
                **models.User._default_values(),
            ),
        )

        current_user = self._database.users.get_user(
            user_id=call.from_user.id,
        )

        try:
            match call.data.split():
                case ["start"]:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.start(
                            user=call.from_user,
                        ),
                        reply_markup=self._keyboards.start(),
                    )
                case ["view_schedules"]:
                    if not self._data.schedule:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_unavailable(),
                            show_alert=True,
                        )
                    elif not current_user.group:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.group_not_selected(),
                            show_alert=True,
                        )
                    else:
                        await self._bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=self._strings.menu.view_schedules(),
                            reply_markup=self._keyboards.view_schedules(),
                        )
                case ["schedule", current_date]:
                    current_date = utils.get_date_from_callback(current_date)

                    if not self._data.schedule:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_unavailable(),
                            show_alert=True,
                        )
                    elif not current_user.group:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.group_not_selected(),
                            show_alert=True,
                        )
                    else:
                        current_substitutions = self._data.get_substitutions(
                            date=current_date,
                        )

                        await self._bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=self._strings.menu.schedule(
                                date=current_date,
                                schedule=schedule_parser.utils.get_schedule_with_substitutions(
                                    schedule=self._data.schedule,
                                    substitutions=current_substitutions,
                                    group=current_user.group,
                                    date=current_date,
                                ),
                                has_substitutions=bool(current_substitutions),
                            ),
                            reply_markup=self._keyboards.schedule(),
                        )
                case ["view_groups", current_page]:
                    current_page = int(current_page)

                    if not self._data.schedule:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_unavailable(),
                            show_alert=True,
                        )
                    else:
                        await self._bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=self._strings.menu.view_groups(),
                            reply_markup=self._keyboards.view_groups(
                                groups=self._data.schedule,
                                page=current_page,
                            ),
                        )
                case ["group", *current_group]:
                    current_group = " ".join(current_group)

                    self._database.users.edit_group(
                        user_id=current_user.id,
                        group=current_group,
                    )

                    await self._bot.answer_callback_query(
                        callback_query_id=call.id,
                        text=self._strings.alert.group_selected(
                            group=current_group,
                        ),
                        show_alert=True,
                    )
                case ["settings"]:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.settings(
                            user=current_user,
                        ),
                        reply_markup=self._keyboards.settings(
                            user=current_user,
                        ),
                    )
                case ["settings_switch", current_setting]:
                    getattr(self._database.users, f"edit_{current_setting}")(
                        current_user.id,
                        not (getattr(current_user, current_setting)),
                    )

                    current_user = self._database.users.get_user(
                        user_id=current_user.id,
                    )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.settings(
                            user=current_user,
                        ),
                        reply_markup=self._keyboards.settings(
                            user=current_user,
                        ),
                    )
                case ["admin"] if is_admin:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.admin(
                            user=call.from_user,
                            time_started=pyquoks.utils.get_process_created_datetime(),
                        ),
                        reply_markup=self._keyboards.admin(),
                    )
                case ["manage_schedule"] if is_admin:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_schedule(
                            schedule=self._data.schedule,
                        ),
                        reply_markup=self._keyboards.manage_schedule(),
                    )
                case ["upload_schedule"] if is_admin:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.upload_schedule(
                            workbook_extension=self._config.settings.workbook_extension,
                        ),
                        reply_markup=self._keyboards.upload_schedule(),
                    )

                    await state.set_state(data.States.upload_schedule)
                case ["delete_schedule"] if is_admin:
                    if not self._data.schedule:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_unavailable(),
                            show_alert=True,
                        )
                    else:
                        self._data.update(
                            schedule=[],
                        )

                        await self._bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=self._strings.menu.manage_schedule(
                                schedule=self._data.schedule,
                            ),
                            reply_markup=self._keyboards.manage_schedule(),
                        )

                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_deleted(),
                            show_alert=True,
                        )
                case ["view_substitutions"] if is_admin:
                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.view_substitutions(),
                        reply_markup=self._keyboards.select_substitutions(),
                    )
                case ["manage_substitutions", current_date] if is_admin:
                    current_date = utils.get_date_from_callback(current_date)

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_substitutions(
                            date=current_date,
                            substitutions=self._data.get_substitutions(
                                date=current_date,
                            ),
                        ),
                        reply_markup=self._keyboards.manage_substitutions(
                            date=current_date,
                        ),
                    )
                case ["upload_substitutions", current_date] if is_admin:
                    current_date = utils.get_date_from_callback(current_date)

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.upload_substitutions(
                            date=current_date,
                            workbook_extension=self._config.settings.workbook_extension,
                        ),
                        reply_markup=self._keyboards.upload_substitutions(
                            date=current_date,
                        ),
                    )

                    await state.set_state(data.States.upload_substitutions)
                    await state.set_data(
                        data={
                            "current_date": current_date,
                        },
                    )
                case ["delete_substitutions", current_date] if is_admin:
                    current_date = utils.get_date_from_callback(current_date)

                    current_substitutions = self._data.get_substitutions(current_date)

                    if not current_substitutions:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.substitutions_unavailable(),
                            show_alert=True,
                        )
                    else:
                        self._data.update_substitutions(
                            date=current_date,
                            substitutions=[],
                        )

                        current_substitutions = self._data.get_substitutions(current_date)

                        await self._bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=self._strings.menu.manage_substitutions(
                                date=current_date,
                                substitutions=current_substitutions,
                            ),
                            reply_markup=self._keyboards.manage_substitutions(
                                date=current_date,
                            ),
                        )

                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.substitutions_deleted(),
                            show_alert=True,
                        )
                case ["export_logs"] if is_admin:
                    if not self._config.settings.file_logging:
                        await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.export_logs_unavailable(),
                            show_alert=True,
                        )
                    else:
                        logs_file = self._logger.file

                        await self._bot.send_document(
                            chat_id=call.message.chat.id,
                            message_thread_id=utils.get_message_thread_id(call.message),
                            document=aiogram.types.BufferedInputFile(
                                file=logs_file.read(),
                                filename=logs_file.name,
                            ),
                        )

                        logs_file.close()
                case ["answer_callback"]:
                    await self._bot.answer_callback_query(
                        callback_query_id=call.id,
                    )
                case _:
                    await self._bot.answer_callback_query(
                        callback_query_id=call.id,
                        text=self._strings.alert.button_unavailable(),
                        show_alert=True,
                    )
        except Exception as exception:
            if type(exception) not in constants.IGNORED_EXCEPTIONS:
                self._logger.log_error(exception)
        finally:
            await self._bot.answer_callback_query(
                callback_query_id=call.id,
            )

    # endregion
