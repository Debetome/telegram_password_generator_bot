from enum import Enum

from string import digits
from string import ascii_letters
from string import ascii_uppercase
from string import ascii_lowercase

class Characters:
    LOWER_UPPER = ascii_letters
    LOWER_DIGITS = "".join([ascii_lowercase, digits])
    UPPER_DIGITS = "".join([ascii_uppercase, digits])
    LOWER_UPPER_DIGITS = "".join([ascii_letters, digits])
    ALL = "".join(["abcdefghABCDEFGH", digits, "!\"~$@^'*+-*{}=_"])
    ONLY_DIGITS = digits

class GenerateState(int, Enum):
    SELECT_CHARS = 1
    SELECT_LENGTH = 2
    SAVE_PASSWORD = 3
    RETRIEVE_TITLE = 4

class SaveState(int, Enum):
    RETRIEVE_PASS = 1
    RETRIEVE_TITLE = 2

class EditState(int, Enum):
    SELECT_PASSWORD = 1
    SELECT_OPTION = 2
    RETRIEVE_VALUE = 3

class ExportState(int, Enum):
    pass

class MyPasswordState(int, Enum):
    SELECT_PASSWORD = 1
    SELECT_PASSWORD_OPTIONS = 2
    EDIT_PASSWORD = 3
    EDIT_RETRIEVE_VALUE = 4
    DELETE_PASSWORD = 5

class DeletePassword(int, Enum):
    SELECT_PASSWORD = 1
    CONFIRM_DELETION = 2
