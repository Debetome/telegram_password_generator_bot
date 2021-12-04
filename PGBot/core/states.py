from enum import Enum

class GenerateState(int, Enum):
    SELECT_CHARS = 1
    SELECT_LENGTH = 2
    SAVE_PASSWORD = 3

class SaveState(int, Enum):
    RETRIEVE_PASS = 1
    RETRIEVE_TITLE = 2

class MyPasswordState(int, Enum):
    SELECT_PASSWORD = 1
    SELECT_PASSWORD_OPTIONS = 2

class DeletePassword(int, Enum):
    SELECT_PASSWORD = 1
