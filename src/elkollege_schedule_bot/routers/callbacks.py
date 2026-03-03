import aiogram
import aiogram.fsm.context
import pyquoks.utils
import schedule_parser.models

from .. import constants
from .. import models
from .. import states
from .. import utils
from ..managers import config
from ..managers import database
from ..providers import keyboards
from ..providers import strings
from ..services import logger


class CallbacksRouter(aiogram.Router):
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

        self.callback_query.register(
            self._callback_handler,
        )

        self._logger.info(f"{self.name} initialized!")

    # region Handlers

    async def _callback_handler(
            self,
            call: aiogram.types.CallbackQuery,
            state: aiogram.fsm.context.FSMContext,
    ) -> bool | None:
        is_admin = call.from_user.id in self._config.settings.admins_list

        self._logger.log_user_interaction(
            user=call.from_user,
            interaction=f"{call.data} ({is_admin=})",
        )

        await state.clear()

        self._database.users.add_user(
            _id=call.from_user.id,
            **models.DatabaseUser._default_values(),
        )

        current_user = self._database.users.get_user(
            _id=call.from_user.id,
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
                    current_schedule = self._database.schedules.get_schedule()

                    if not current_schedule:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_missing(),
                            show_alert=True,
                        )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.alert.view_schedules(),
                        reply_markup=self._keyboards.view_schedules(),
                    )
                case ["schedule", current_timestamp]:
                    current_timestamp = int(current_timestamp)
                    current_date = utils.get_date_from_timestamp(current_timestamp)

                    current_schedule = self._database.schedules.get_schedule()

                    if not current_schedule:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_missing(),
                            show_alert=True,
                        )

                    if not current_user.group_name:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.group_not_selected(),
                            show_alert=True,
                        )

                    try:
                        current_group_schedule = current_schedule.get_group_schedule_by_group_name(
                            group_name=current_user.group_name,
                        )
                    except StopIteration:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.group_missing_in_schedule(),
                            show_alert=True,
                        )

                    try:
                        current_day_schedule = current_group_schedule.get_day_schedule_by_weekday(
                            weekday=current_date.weekday(),
                        )
                    except StopIteration:
                        current_day_schedule = schedule_parser.models.DaySchedule(
                            weekday=current_date.weekday(),
                            periods_list=[],
                        )

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    current_substitutions_list = current_substitution.get_substitutions_by_group_name(
                        group_name=current_user.group_name,
                    )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.schedule(
                            date=current_date,
                            schedule=schedule_parser.utils.apply_substitutions_to_schedule(
                                schedule=current_day_schedule.periods_list,
                                substitutions=current_substitutions_list,
                            ),
                            has_substitutions=bool(current_substitutions_list),
                        ),
                        reply_markup=self._keyboards.schedule(),
                    )
                case ["view_groups", current_page]:
                    current_page = int(current_page)

                    current_schedule = self._database.schedules.get_schedule()

                    if not current_schedule:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_missing(),
                            show_alert=True,
                        )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.view_groups(),
                        reply_markup=self._keyboards.view_groups(
                            groups=current_schedule.groups_list,
                            current_page=current_page,
                        ),
                    )
                case ["group", *current_group_name]:
                    current_group_name = " ".join(current_group_name)

                    self._database.users.edit_group_name(
                        _id=current_user.id,
                        group_name=current_group_name,
                    )

                    current_user = self._database.users.get_user(
                        _id=current_user.id,
                    )

                    await self._bot.answer_callback_query(
                        callback_query_id=call.id,
                        text=self._strings.alert.group_selected(
                            group_name=current_user.group_name,
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
                    self._database.users._edit_setting(
                        _id=current_user.id,
                        setting=current_setting,
                        value=not getattr(current_user, current_setting),
                    )

                    current_user = self._database.users.get_user(
                        _id=current_user.id,
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
                            date_started=pyquoks.utils.get_process_created_datetime(),
                        ),
                        reply_markup=self._keyboards.admin(),
                    )
                case ["manage_schedule"] if is_admin:
                    current_schedule = self._database.schedules.get_schedule()

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_schedule(
                            schedule=current_schedule.groups_list if current_schedule else [],
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

                    await state.set_state(states.upload_substitutions)
                case ["delete_schedule"] if is_admin:
                    current_schedule = self._database.schedules.get_schedule()

                    if not current_schedule:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.schedule_missing(),
                            show_alert=True,
                        )

                    self._database.schedules.delete_schedule()

                    current_schedule = self._database.schedules.get_schedule()

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_schedule(
                            schedule=current_schedule.groups_list,
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
                        reply_markup=self._keyboards.view_substitutions(),
                    )
                case ["manage_substitutions", current_timestamp] if is_admin:
                    current_timestamp = int(current_timestamp)
                    current_date = utils.get_date_from_timestamp(current_timestamp)

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_substitutions(
                            date=current_date,
                            substitutions=current_substitution.substitutions_list,
                        ),
                        reply_markup=self._keyboards.manage_substitutions(
                            date=current_date,
                        ),
                    )
                case ["upload_substitutions", current_timestamp] if is_admin:
                    current_timestamp = int(current_timestamp)
                    current_date = utils.get_date_from_timestamp(current_timestamp)

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

                    await state.set_state(states.upload_substitutions)
                    await state.set_data(
                        data={
                            "current_date": current_date,
                        },
                    )
                case ["delete_substitutions", current_timestamp] if is_admin:
                    current_timestamp = int(current_timestamp)
                    current_date = utils.get_date_from_timestamp(current_timestamp)

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    if not current_substitution:
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.substitutions_missing(),
                            show_alert=True,
                        )

                    self._database.substitutions.delete_substitutions()

                    current_substitution = self._database.substitutions.get_substitution(
                        timestamp=current_timestamp,
                    )

                    await self._bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=self._strings.menu.manage_substitutions(
                            date=current_date,
                            substitutions=current_substitution.substitutions_list,
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
                        return await self._bot.answer_callback_query(
                            callback_query_id=call.id,
                            text=self._strings.alert.logging_disabled(),
                            show_alert=True,
                        )

                    with self._logger.file as logs_file:
                        await self._bot.send_document(
                            chat_id=call.message.chat.id,
                            message_thread_id=utils.get_message_thread_id(call.message),
                            document=aiogram.types.BufferedInputFile(
                                file=logs_file.read(),
                                filename=logs_file.name,
                            ),
                        )
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
                self._logger.log_exception(exception)
        finally:
            await self._bot.answer_callback_query(
                callback_query_id=call.id,
            )

    # endregion
