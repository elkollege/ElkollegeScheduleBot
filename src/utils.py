from __future__ import annotations

import aiogram


def get_message_thread_id(message: aiogram.types.Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.is_topic_message:
        return message.reply_to_message.message_thread_id
    elif message.is_topic_message:
        return message.message_thread_id
    else:
        return None
