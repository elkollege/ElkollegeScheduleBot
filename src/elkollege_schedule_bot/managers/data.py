import datetime
import json
import os

import pyquoks
import schedule_parser

import elkollege_schedule_bot.utils


class DataManager(pyquoks.managers.data.DataManager):
    schedule: list[schedule_parser.models.GroupSchedule]

    def get_substitutions(self, date: datetime.datetime) -> list[schedule_parser.models.Substitution]:
        try:
            with open(
                    self._PATH + self._FILENAME.format(
                        f"substitutions_{elkollege_schedule_bot.utils.get_callback_date(date)}"),
                    "rb",
            ) as file:
                data = json.loads(file.read())

                return [schedule_parser.models.Substitution(**model) for model in data]
        except Exception:
            return []

    def update_substitutions(
            self,
            date: datetime.datetime,
            substitutions: list[schedule_parser.models.Substitution],
    ) -> None:
        os.makedirs(
            name=self._PATH,
            exist_ok=True,
        )

        with open(
                self._PATH + self._FILENAME.format(
                    f"substitutions_{elkollege_schedule_bot.utils.get_callback_date(date)}"),
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                [model.model_dump() for model in substitutions],
                fp=file,
                ensure_ascii=False,
                indent=2,
            )
