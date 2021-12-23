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

    def create_database(self) -> None:
        if os.path.exists(self._database):
            return None

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
            passwords.append(PasswordRegister(*password))

        return passwords

    def insert_user(self, user: User) -> None:
        firstname = user.firstname
        lastname = user.lastname
        chat_id = user.chat_id

        self._execute(f"INSERT INTO Users(Firstname, Lastname, Chat_id) VALUES(\"{firstname}\", \"{lastname}\", \"{chat_id}\")")
        self._response = f"Inserted new user '{firstname} {lastname}' from chat id '{chat_id}'"

    def insert_password(self, password: PasswordRegister) -> None:
        title = password.title
        passwd = password.password
        user_id = password.user_id

        self._execute(f"INSERT INTO Passwords(Title, Password, User_id) VALUES(\"{title}\", \"{passwd}\", \"{user_id}\")")
        self._response = f"Inserted new password '{password}' titled '{title}' belongging to user of id '{user_id}'"

    def update_user(self, user: User) -> None:
        id = user.id
        firstname = user.firstname
        lastname = user.lastname
        chat_id = user.chat_id

        self._execute(f"UPDATE Users SET Firstname=\"{firstname}\" Lastname=\"{lastname}\" Chat_id=\"{chat_id}\" WHERE Id=\"{id}\"")
        self._response = f"Updated user of '{id}'"

    def update_password(self, password: PasswordRegister) -> None:
        id = password.id
        title = password.title
        password = password.password
        user_id = password.user_id

        self._execute(f"UPDATE Passwords SET Title=\"{title}\" Password=\"{password}\" User_id=\"{user_id}\" WHERE Id=\"{id}\"")
        self._response = f"Updated password of id '{id}' belongging to user of id '{user_id}'"

    def delete_user(self, user: User) -> None:
        id = user.id
        firstname = user.firstname
        lastname = user.lastname
        chat_id = user.chat_id
        self._execute(f"DELETE INTO Users WHERE Id=\"{id}\"")
        self._response = f"Deleted user '{firstname} {lastname}' of id '{id}'"

    def delete_password(self, password: PasswordRegister) -> None:
        id = password.id
        user_id = password.user_id
        self._execute(f"DELETE INTO Passwords WHERE Id=\"{id}\"")
        self._response = f"Deleted password titled '{title}' belongging to user of id '{user_id}'"

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

    def _execute(self, command: str, fetchone=False) -> None:
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
