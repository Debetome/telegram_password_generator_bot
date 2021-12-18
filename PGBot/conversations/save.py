from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)

from PGBot.core.conversation import BaseConversation
from PGBot.core.logger import logger

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.cryptoHandler import CryptoHandler

from PGBot.constants import SaveState
from PGBot.models import PasswordRegister

class SaveConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler
        self.passwordRegister = None

    def _save_password(self):
        if isinstance(self.passwordRegister, PasswordRegister):
            password = self.passwordRegister
            self.dbHandler.insert_password(password)

    def start(self, update: Update, context: CallbackContext):
        self.passwordRegister = PasswordRegister()
        update.message.reply_text("Send password to save ...")
        return SaveState.RETRIEVE_PASS

    def retrieve_password(self, update: Update, context: CallbackContext):
        self.passwordRegister.password = update.message.text

        if len(self.passwordRegister.password) < 8:
            update.message.reply_text("Password can't be lower than 8 characters!")
            return SaveState.RETRIEVE_PASS

        update.message.reply_text("Set a title for this password")
        return SaveState.RETRIEVE_TITLE

    def retrieve_title(self, update: Update, context: CallbackContext):
        self.passwordRegister.title = update.message.text
        self.passwordRegister.chat_id = update.message.chat_id
        self._save_password()

        update.message.reply_text("Password saved!")
        return SaveState.RETRIEVE_PASS

    def cancel(self, update: Update, context: CallbackContext):
        update.message.edit_text("Operation cancelled!")
        return SaveState.RETRIEVE_PASS

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("save", self.start)],
            states={
                SaveState.RETRIEVE_PASS: [CallbackQueryHandler(self.retrieve_password)],
                SaveState.RETRIEVE_TITLE: [CallbackQueryHandler(self.retrieve_title)]
            },
            fallbacks=[
                CommandHandler("save", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )

        self.set_conversation(conversation)
