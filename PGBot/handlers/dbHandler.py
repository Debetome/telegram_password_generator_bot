import sqlite3
import os

from typing import List, Union 
from PGBot.models import *
from PGBot.tables import *

class DatabaseHandler:
    def __init__(self, database="database.db"):
        self._database = database
        self._response = None
        self._conn = None
        self._cursor = None

    def create_database(self):
        if os.path.exists(self._database):
            return

        for table in TABLES.values():
            self._execute(table)

    def get_passwords(self, chat_id: int) -> List[tuple]:
        self._execute(f"SELECT * FROM Passwords WHERE chat_id='{chat_id}'")
        return self._response

    def get_password(self, chat_id: int, title: str) -> tuple:
        self._execute(f"SELECT * FROM Passwords WHERE chat_id='{chat_id}' title='{title}'", fetchone=True)

    def insert_password(self, password: Password) -> None:
        title = password.title
        passwd = password.password
        chat_id = password.chat_id

        self._execute(f"INSERT INTO Passwords(Title, Password, Chat_id) VALUES(\"{title}\", \"{passwd}\", \"{chat_id}\")")
        self._response = f"New password inserted {password}"

    @property
    def database(self) -> str:
        return self._database

    @property
    def response(self) -> Union[Union[str, tuple], None]:
        return self._response

    def _execute(self, command: str, fetchone=False) -> Union[List[str], str]:
        self._connect()

        if not fetchone:
            self._response = self._cursor.execute(command).fetchall()
        else:
            self._response = self._cursor.execute(command).fetchone()

        self._disconnect()

    def _connect(self):
        self._conn = sqlite3.connect(self.database)
        self._cursor = self._conn.cursor()

    def _disconnect(self):
        self._cursor.close()
        self._conn.commit()
        self._conn.close()
