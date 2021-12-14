from PGBot.core.exporter import BaseExporter
from PGBot.models import PasswordRegister

class TxtExporter(BaseExpoter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._format = "txt"
        self._fix_filename()

    def _get_passwords(self, user_id: int) -> PasswordRegister:
        for password in self._dbHandler.get_passwords(user_id):
            yield password

    def _strigify_passwords(self, user_id: int) -> str:
        for i, password in enumerate(self._get_passwords(user_id)):
            content = f"Id: {i}"
            content += f"\nTitle: {password.title}"
            content += f"\nPassword: {password.title}"
            yield content

    def export(self, user_id: int):
        passwords = [p for p in self._strinfify_passwords(user_id)]
        with open(self.filename, "w+") as f:
            f.write("\n".join(passwords))
