from string import digits
from string import ascii_letters
from string import ascii_uppercase
from string import ascii_lowercase

LOWER_UPPER = ascii_letters
LOWER_DIGITS = "".join([ascii_lowercase, digits])
UPPER_DIGITS = "".join([ascii_uppercase, digits])
LOWER_UPPER_DIGITS = "".join([ascii_letters, digits])
ALL = "".join(["abcdefghABCDEFGH", digits, "!\"#~$@^'*+-*{}=_"])
ONLY_DIGITS = digits
