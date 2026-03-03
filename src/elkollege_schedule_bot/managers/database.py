import pyquoks.managers.database
import pyquoks.utils

from .. import models


class DatabaseManager(pyquoks.managers.database.DatabaseManager):
    users: UsersDatabase


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

    def add_user(self, user: models.User) -> None:
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
                user.id,
                user.group_name,
                user.is_notifiable,
            ),
        )

        self.commit()

    def get_user(self, user_id: int) -> models.User | None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                SELECT * FROM {self._NAME} WHERE id = ?
                """,
            ),
            (
                user_id,
            ),
        )
        result = cursor.fetchone()

        if result:
            return models.User.model_validate(dict(result))
        else:
            return None

    def get_users(self) -> list[models.User]:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    SELECT * FROM {self._NAME}
                """,
            ),
        )
        results = cursor.fetchall()

        return [models.User.model_validate(dict(result)) for result in results]

    def edit_group_name(self, user_id: int, group_name: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET group_name = ? WHERE id = ?
                """,
            ),
            (
                group_name,
                user_id,
            ),
        )

        self.commit()

    def edit_is_notifiable(self, user_id: int, is_notifiable: bool) -> None:
        cursor = self.cursor()

        cursor.execute(
            pyquoks.utils.format_multiline_string(
                f"""
                    UPDATE {self._NAME} SET is_notifiable = ? WHERE id = ?
                """,
            ),
            (
                is_notifiable,
                user_id,
            ),
        )

        self.commit()

    def _edit_setting(self, user_id: int, setting: str, value: bool) -> None:
        edit_callable = getattr(self, f"edit_{setting}", None)

        if edit_callable:
            return edit_callable(user_id, value)
        else:
            raise AttributeError(
                name=setting,
                obj=self,
            )
