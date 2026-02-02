import pydantic


# region models

class User(pydantic.BaseModel):
    id: int
    group: str
    is_notifiable: bool

    @staticmethod
    def _default_values() -> dict:
        return {
            "group": "",
            "is_notifiable": True,
        }

    @staticmethod
    def _switchable_values() -> set:
        return {
            "is_notifiable",
        }

# endregion
