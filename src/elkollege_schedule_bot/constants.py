import aiogram.exceptions

FIRST_PAGE = 1
GROUPS_PER_PAGE = 5
GROUPS_PER_ROW = 1
SCHEDULE_DAYS = 3
SETTINGS_PER_ROW = 1

DATE_FORMAT_CALLBACK = "%d_%m_%y"
DATE_FORMAT_READABLE = "%d.%m.%y"
DATE_FORMAT_STARTED = "%d.%m.%y %H:%M:%S"

IGNORED_EXCEPTIONS = (
    aiogram.exceptions.TelegramForbiddenError,
    aiogram.exceptions.TelegramRetryAfter,
)
