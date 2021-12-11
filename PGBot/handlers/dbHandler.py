import sqlite3
import os

from typing import List, Union, Any

from PGBot.models import PasswordRegister
from PGBot.models import User
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

    def get_user(self, user_id: int) -> User:
        self._execute(f"SELECT * FROM Users WHERE Id=\"{user_id}\"", fetchone=True)
        return User(*self._response)

    def get_users(self) -> List[User]:
        self._execute("SELECT * FROM Users")

        users: List[User] = []
        for user in self._response:
            users.append(User(*user))

        return users

    def get_password(self, password_id: int) -> PasswordRegister:
        self._execute(f"SELECT * FROM Passwords WHERE Id=\"{password_id}\"")
        return PasswordRegister(*self._response)

    def get_passwords(self, chat_id: int) -> List[PasswordRegister]:
        self._execute(f"SELECT * FROM Passwords WHERE chat_id='{chat_id}'")

        passwords: List[PasswordRegister] = []
        for password in self._response:
            passwords.append(PasswordRegister(
                id=int(password[0]),
                title=password[1],
                password=password[2],
                chat_id=int(password[3])
            ))

        return passwords

    def insert_user(self, user: User) -> None:
        firstname = user.firstname
        lastname = user.lastname
        chat_id = user.chat_id

        self._execute(f"INSERT INTO Users(Firstname, Lastname, Chat_id) VALUES(\"{firstname}\", \"{lastname}\", \"{chat_id}\")")
        self._response = f"New user {firstname} {lastname} inserted!"

    def insert_password(self, password: PasswordRegister) -> None:
        title = password.title
        passwd = password.password
        chat_id = password.chat_id

        self._execute(f"INSERT INTO Passwords(Title, Password, Chat_id) VALUES(\"{title}\", \"{passwd}\", \"{chat_id}\")")
        self._response = f"New password inserted {password}"

    def delete_user(self, user: User) -> None:
        firstname = user.firstname
        lastname = user.lastname
        chat_id = user.chat_id
        self._execute(f"DELETE INTO Users WHERE Chat_id=\"{chat_id}\"")
        self._response = f"User {firstname} {lastname} deleted!"

    def delete_password(self, password: PasswordRegister) -> None:
        title = password.title
        self._execute(f"DELETE INTO Passwords WHERE Title=\"{title}\"")
        self._response = "Password titled '{title}' deleted!"

    @property
    def database(self) -> str:
        return self._database

    @property
    def response(self) -> Union[Union[str, tuple], None]:
        return self._response

    @property
    def connection(self) -> Any:
        return self._conn

    @property
    def cursor(self) -> Any:
        return self._cursor

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
