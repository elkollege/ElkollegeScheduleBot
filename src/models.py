import enum

import pydantic


# region Enums

class BellsVariants(enum.Enum):
    Monday = 0
    Wednesday = 1
    Other = 2


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
