import csv

from PGBot.core.exporter import BaseExporter
from PGBot.models import PasswordRegister
from typing import Dict, List, Union

class CsvExporter(BaseExporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._format = "csv"
        self._fix_filename()

    def _get_passwords(self, user_id: int) -> PasswordRegister:
        for password in self._dbHandler.get_passwords(user_id):
            yield password

    def _get_table_fields(self) -> List[str]:
        return [
            "Id",
            "Title",
            "Password"
        ]

    def _parse_passwords(self, user_id: int) -> Dict[str, Union[str, int]]:
        for i, password in enumerate(self._get_passwords(user_id)):
            dict_password = {}

            dict_password["id"] = i
            dict_password["title"] = password.title
            dict_password["password"] = password.password

            yield dict_password

    def export(self, user_id: int):
        with open(self._filename, "w+") as f:
            writer = csv.DictWriter(f, fieldnames=self._get_fields())
            writer.writeheader()

            for password in self._parse_passwords(user_id):
                writer.writerow(password)

