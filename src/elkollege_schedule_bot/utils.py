import datetime

import aiogram

from . import constants


def get_message_thread_id(message: aiogram.types.Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.is_topic_message:
        return message.reply_to_message.message_thread_id
    elif message.is_topic_message:
        return message.message_thread_id
    else:
        return None


def get_readable_date(date: datetime.datetime) -> str:
    return date.strftime(constants.DATE_FORMAT_READABLE)


def get_timestamp_from_date(date: datetime.datetime) -> int:
    return int(date.timestamp())


def get_date_from_timestamp(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)
