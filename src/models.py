import enum

import pydantic


# region Enums

class BellsType(enum.Enum):
    MONDAY = 0
    WEDNESDAY = 1
    OTHER = 2


# endregion

# region models

class User(pydantic.BaseModel):
    id: int
    group: str | None

    @staticmethod
    def _default_values() -> dict:
        return {
            "group": None,
        }

# endregion
