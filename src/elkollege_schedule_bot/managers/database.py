import textwrap

import pyquoks

from .. import models


class DatabaseManager(pyquoks.managers.database.DatabaseManager):
    users: UsersDatabase


class UsersDatabase(pyquoks.managers.database.Database):
    _NAME = "users"

    _SQL = textwrap.dedent(
        f"""\
        CREATE TABLE IF NOT EXISTS {_NAME} (
        id INTEGER PRIMARY KEY NOT NULL,
        `group` TEXT NOT NULL,
        is_notifiable BOOLEAN NOT NULL
        )
        """,
    ).rstrip()

    def add_user(self, user: models.User) -> None:
        cursor = self.cursor()

        cursor.execute(
            textwrap.dedent(
                f"""\
                INSERT OR IGNORE INTO {self._NAME} (
                id,
                `group`,
                is_notifiable
                )
                VALUES (?, ?, ?)
                """,
            ).rstrip(),
            (
                user.id,
                user.group,
                user.is_notifiable,
            ),
        )

        self.commit()

    def get_user(self, user_id: int) -> models.User | None:
        cursor = self.cursor()

        cursor.execute(
            textwrap.dedent(
                f"""\
                SELECT * FROM {self._NAME} WHERE id = ?
                """,
            ).rstrip(),
            (
                user_id,
            ),
        )
        result = cursor.fetchone()

        if result:
            return models.User(**dict(result))
        else:
            return None

    def get_users(self) -> list[models.User]:
        cursor = self.cursor()

        cursor.execute(
            textwrap.dedent(
                f"""\
                SELECT * FROM {self._NAME}
                """,
            ).rstrip(),
        )
        results = cursor.fetchall()

        return [models.User(**dict(result)) for result in results]

    def edit_group(self, user_id: int, group: str) -> None:
        cursor = self.cursor()

        cursor.execute(
            textwrap.dedent(
                f"""\
                UPDATE {self._NAME} SET `group` = ? WHERE id = ?
                """,
            ).rstrip(),
            (
                group,
                user_id,
            ),
        )

        self.commit()

    def edit_is_notifiable(self, user_id: int, is_notifiable: bool) -> None:
        cursor = self.cursor()

        cursor.execute(
            textwrap.dedent(
                f"""\
                UPDATE {self._NAME} SET is_notifiable = ? WHERE id = ?
                """,
            ).rstrip(),
            (
                is_notifiable,
                user_id,
            ),
        )

        self.commit()

    def _edit_setting(self, user_id: int, setting: str, value: bool) -> None:
        edit_callable = getattr(self, f"edit_{setting}", None)

        if edit_callable is None:
            raise AttributeError(
                name=setting,
                obj=self,
            )
        else:
            return edit_callable(
                user_id,
                value,
            )
