from abc import ABCMeta, abstractmethod

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.cryptoHandler import CryptoHandler

class BaseExporter(metaclass=ABCMeta):
    def __init__(
            self, 
            filename: str, 
            dbHandler: DatabaseHandler, 
            crypto: CryptoHandler
        ):
        self._filename = filename
        self._dbHandler = dbHandler
        self._cryptoHandler = crypto
        self._format = None

    def _set_filename(self, filename: str):
        if len(filename.split(".")) > 1:
            self._filename = filename

    def _fix_filename(self):
        if self._format is None:
            return

        if len(self.filename.split(".")) > 1:
            if not re.match(self.filename.split(".")[1], self._format):
                self._set_filename(".".join([self._filename.split(".")[0], self._format]))
                return
            else:
                return

        self._set_filename(".".join([self.filename, self.format]))

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def dbHandler(self) -> DatabaseHandler:
        return self._dbHandler

    @property
    def cryptoHandler(self) -> CryptoHandler:
        return self._cryptoHandler

    @abstractmethod
    def export(self, user_id: int):
        pass
