import datetime
import json
import os

import pyquoks
import schedule_parser

from .. import utils


class DataManager(pyquoks.managers.data.DataManager):
    schedule: list[schedule_parser.models.GroupSchedule]

    def _get_substitutions_filename(self, date: datetime.datetime) -> str:
        string_date = utils.get_callback_date(date)

        return self._FILENAME.format(f"substitutions_{string_date}")

    def get_substitutions(self, date: datetime.datetime) -> list[schedule_parser.models.Substitution]:
        try:
            with open(self._PATH + self._get_substitutions_filename(date), "rb") as file:
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

        with open(self._PATH + self._get_substitutions_filename(date), "w", encoding="utf-8") as file:
            json.dump(
                [model.model_dump() for model in substitutions],
                file,
                ensure_ascii=False,
                indent=2,
            )
