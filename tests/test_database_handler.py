import unittest

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.models import PasswordRegister 

handler = DatabaseHandler("test_database.db")

class TestDatabaseHandler(unittest.TestCase):
    def test_create_database(self):
        try:
            handler.create_database()
            print("[+] Database created!")
        except Exception as ex:
            raise Exception(ex)

    def test_insert_password(self):
        try:
            test_password = PasswordRegister()
            test_password.title = "Email"
            test_password.password = "123456789"
            test_password.chat_id = 123456

            handler.insert_password(test_password)
            print("[+] Test password inserted!")

        except Exception as ex:
            raise Exception(ex)

    def test_get_passwords(self):
        try:
            chat_id = 123456
            passwords = handler.get_passwords(chat_id)
            print(passwords)
            print("[+] Passwords gotten!")

        except Exception as ex:
            raise Exception(ex)

    def test_get_password(self):
        try:
            chat_id = 123456
            password = handler.get_password(chat_id, "Email")
            print(f"[*] Password: {password}")
            print("[+] Password gotten!")

        except Exception as ex:
            raise Exception(ex)
