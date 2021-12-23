from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

from PGBot.core.logger import logger
from PGBot.core.conversation import BaseConversation
from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.encryptHandler import EncryptHandler

from PGBot.models import PasswordRegister
from PGBot.constants import ExportState

class ExportConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, encryptHandler: EncryptHandler):
        self.dbHandler = dbHandler
        self.encryptHandler = encryptHandler
        self.register = None

    def start(self, update: Update, context: CallbackContext):
        return None

    def cancel(self, update: Update, context: CallbackContext):
        return None

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("export", self.start)],
            states={},
            fallbacks=[
                CommandHandler("start", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )

        self.set_conversation(conversation)
