import base64
import random
import os

from typing import Union
from string import ascii_letters
from string import digits

from cryptography.exceptions import AlreadyFinalized
from cryptography.exceptions import InvalidTag
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptHandler:
    def __init__(self):
        self._public_key = None
        self._private_key = None

    def _generate_salt(self):
        pass

    def _generate_random_bytes(self):
        pass

    def _get_password_bytes(self):
        pass

    def _encode(self, context: bytes) -> bytes:
        pass

    def _decode(self, context: bytes) -> bytes:
        pass

    def encrypt(self, plaintext: str, key: str):
        pass

    def decrypt(self, cyphertext: str, key: str):
        pass
