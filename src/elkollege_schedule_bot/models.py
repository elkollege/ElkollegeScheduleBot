import pydantic


# region Models

class DatabaseSchedules(pydantic.BaseModel):
    id: int
    building_id: int
    json: str


class DatabaseSubstitutions(pydantic.BaseModel):
    id: int
    building_id: int
    timestamp: int
    json: str


class DatabaseUser(pydantic.BaseModel):
    id: int
    group_name: str
    is_notifiable: bool

    @staticmethod
    def _default_values() -> dict:
        return {
            "group_name": "",
            "is_notifiable": True,
        }

    @staticmethod
    def _switchable_values() -> set:
        return {
            "is_notifiable",
        }

# endregion
