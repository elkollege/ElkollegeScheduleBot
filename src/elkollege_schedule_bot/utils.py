import datetime

import aiogram


def get_message_thread_id(message: aiogram.types.Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.is_topic_message:
        return message.reply_to_message.message_thread_id
    elif message.is_topic_message:
        return message.message_thread_id
    else:
        return None


def get_readable_date(date: datetime.datetime) -> str:
    return date.strftime("%d.%m.%y")


def get_callback_date(date: datetime.datetime) -> str:
    return date.strftime("%d_%m_%y")


def get_date_from_callback(callback: str) -> datetime.datetime:
    return datetime.datetime.strptime(callback, "%d_%m_%y")
