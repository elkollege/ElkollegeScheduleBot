import aiogram.exceptions

FIRST_PAGE = 1
GROUPS_PER_PAGE = 5
GROUPS_PER_ROW = 1
SCHEDULE_DAYS = 2
SUBSTITUTIONS_DAYS = 3

IGNORED_EXCEPTIONS = [
    aiogram.exceptions.TelegramForbiddenError,
    aiogram.exceptions.TelegramRetryAfter,
]
