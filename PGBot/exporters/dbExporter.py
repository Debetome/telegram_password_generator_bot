import sqlite

from PGBot.core.exporter import BaseExporter
from PGBot.models import PasswordRegister
from typing import Dict, List, Union

class DbExporter(BaseExporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._format = "db"
        self._conn = None
        self._cursor = None
        self._fix_filename()

    def _create_table(self):
        self._execute("""
        CREATE TABLE IF NOT EXISTS Passwords(
            \"Id\" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            \"Title\" TEXT NOT NULL,
            \"Password\" TEXT NOT NULL
        )
        """)

    def _get_passwords(self, user_id: int) -> PasswordRegister:
        for password in self._dbHandler.get_passwords(user_id):
            yield password

    def _create_commands(self, user_id: int) -> str:
        for password in self._get_passwords(user_id):
            password = password.password
            title = password.title
            command = f"INSERT INTO Passwords(Title, Password) VALUES(\"{password}\", \"{title}\""
            yield command

    def export(self, user_id: int):
        for command in self._create_commands(user_id):
            self._exec(command)

    def _execute(self, command: str):
        try:
            self._connect()
            self._cursor.execute(f"{command}")
            self._disconnect()

        except Exception as ex:
            raise ValueError(ex)

    def _connect(self):
        self._conn = sqlite.connect(self._filename)
        self._cursor = self._conn.cursor()

    def _disconnect(self):
        self._cursor.close()
        self._conn.commit()
        self._conn.close()
