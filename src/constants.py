import aiogram.exceptions

IGNORED_EXCEPTIONS = [
    aiogram.exceptions.TelegramForbiddenError,
    aiogram.exceptions.TelegramRetryAfter,
]
