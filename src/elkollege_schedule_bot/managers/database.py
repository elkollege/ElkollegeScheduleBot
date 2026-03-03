import pyquoks.managers.database
import pyquoks.utils

from .. import constants
from .. import models


class DatabaseManager(pyquoks.managers.database.DatabaseManager):
    schedules: SchedulesDatabase
    substitutions: SubstitutionsDatabase
    users: UsersDatabase


class SchedulesDatabase(pyquoks.managers.database.Database):
    _NAME = "schedules"

    _SQL = pyquoks.utils.format_multiline_string(
        f"""
            CREATE TABLE IF NOT EXISTS {_NAME} (
            id INTEGER PRIMARY KEY NOT NULL,
            building_id INTEGER NOT NULL,
            json_string TEXT NOT NULL
            )
        """,
    )

    def add_schedule(self, json_string: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    INSERT INTO {self._NAME} (
                    building_id,
                    json_string
                    )
                    VALUES (?, ?)
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
                json_string,
            ),
        )

        self.commit()

    def get_schedule(self) -> models.DatabaseSchedule | None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    SELECT * FROM {self._NAME} WHERE building_id = ?
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
            ),
        )
        result = cursor.fetchone()

        if result:
            return models.DatabaseSchedule.model_validate(dict(result))
        else:
            return None

    def edit_json_string(self, json_string: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET json_string = ? WHERE building_id = ?
                """,
            ),
            (
                json_string,
                constants.TEMP_BUILDING_ID,
            ),
        )

        self.commit()

    def delete_schedule(self) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    DELETE FROM {self._NAME} WHERE building_id = ?
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
            ),
        )

        self.commit()


class SubstitutionsDatabase(pyquoks.managers.database.Database):
    _NAME = "substitutions"

    _SQL = pyquoks.utils.format_multiline_string(
        f"""
            CREATE TABLE IF NOT EXISTS {_NAME} (
            id INTEGER PRIMARY KEY NOT NULL,
            building_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            json_string TEXT NOT NULL
            )
        """,
    )

    def add_substitution(self, timestamp: int, json_string: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    INSERT INTO {self._NAME} (
                    building_id,
                    timestamp,
                    json_string
                    )
                    VALUES (?, ?, ?)
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
                timestamp,
                json_string,
            ),
        )

        self.commit()

    def get_substitution(self, timestamp: int) -> models.DatabaseSubstitution | None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    SELECT * FROM {self._NAME} WHERE building_id = ? AND timestamp = ?
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
                timestamp,
            ),
        )
        result = cursor.fetchone()

        if result:
            return models.DatabaseSubstitution.model_validate(dict(result))
        else:
            return None

    def edit_json_string(self, timestamp: int, json_string: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET json_string = ? WHERE building_id = ? AND timestamp = ?
                """,
            ),
            (
                json_string,
                constants.TEMP_BUILDING_ID,
                timestamp,
            ),
        )

        self.commit()

    def delete_substitution(self, timestamp: int) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    DELETE FROM {self._NAME} WHERE building_id = ? AND timestamp = ?
                """,
            ),
            (
                constants.TEMP_BUILDING_ID,
                timestamp,
            ),
        )

        self.commit()


class UsersDatabase(pyquoks.managers.database.Database):
    _NAME = "users"

    _SQL = pyquoks.utils.format_multiline_string(
        f"""
            CREATE TABLE IF NOT EXISTS {_NAME} (
            id INTEGER PRIMARY KEY NOT NULL,
            group_name TEXT NOT NULL,
            is_notifiable BOOLEAN NOT NULL
            )
        """,
    )

    def add_user(self, _id: int, group_name: str, is_notifiable: bool) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    INSERT OR IGNORE INTO {self._NAME} (
                    id,
                    group_name,
                    is_notifiable
                    )
                    VALUES (?, ?, ?)
                """,
            ),
            (
                _id,
                group_name,
                is_notifiable,
            ),
        )

        self.commit()

    def get_user(self, _id: int) -> models.DatabaseUser | None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    SELECT * FROM {self._NAME} WHERE id = ?
                """,
            ),
            (
                _id,
            ),
        )
        result = cursor.fetchone()

        if result:
            return models.DatabaseUser.model_validate(dict(result))
        else:
            return None

    def get_users_list(self) -> list[models.DatabaseUser]:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    SELECT * FROM {self._NAME}
                """,
            ),
        )
        results = cursor.fetchall()

        return [models.DatabaseUser.model_validate(dict(result)) for result in results]

    def edit_group_name(self, _id: int, group_name: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET group_name = ? WHERE id = ?
                """,
            ),
            (
                group_name,
                _id,
            ),
        )

        self.commit()

    def edit_is_notifiable(self, _id: int, is_notifiable: bool) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET is_notifiable = ? WHERE id = ?
                """,
            ),
            (
                is_notifiable,
                _id,
            ),
        )

        self.commit()

    def _edit_setting(self, _id: int, setting: str, value: bool) -> None:
        edit_callable = getattr(self, f"edit_{setting}", None)

        if edit_callable:
            return edit_callable(_id, value)
        else:
            raise AttributeError(
                name=setting,
                obj=self,
            )
