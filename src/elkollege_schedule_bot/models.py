import json

import pydantic
import schedule_parser.models


# region Models

class DatabaseSchedule(pydantic.BaseModel):
    id: int
    building_id: int
    json_string: str

    @property
    def groups_list(self) -> list[schedule_parser.models.GroupSchedule]:
        return [
            schedule_parser.models.GroupSchedule.model_validate(
                schedule,
            ) for schedule in json.loads(self.json_string)
        ]

    def get_group_schedule_by_group_name(self, group_name: str) -> schedule_parser.models.GroupSchedule:
        return schedule_parser.models.GroupSchedule.get_group_schedule_by_group_name(
            iterable=self.groups_list,
            group_name=group_name,
        )


class DatabaseSubstitution(pydantic.BaseModel):
    id: int
    building_id: int
    timestamp: int
    json_string: str

    @property
    def substitutions_list(self) -> list[schedule_parser.models.Substitution]:
        return [
            schedule_parser.models.Substitution.model_validate(
                substitution,
            ) for substitution in json.loads(self.json_string)
        ]

    def get_substitutions_by_group_name(self, group_name: str) -> list[schedule_parser.models.Substitution]:
        return schedule_parser.models.Substitution.get_substitutions_by_group_name(
            iterable=self.substitutions_list,
            group_name=group_name,
        )


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
