from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import(
    Updater,
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
from PGBot.handlers.cryptoHandler import CryptoHandler

from PGBot.constants import MyPasswordState
from PGBot.models import PasswordRegister

class MyPasswordsConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler

    def start(self, update: Update, context: CallbackContext):
        passwords = self.dbHandler.get_passwords(int(update.message.chat_id))
        passwords_keyboard = []

        for i in range(passwords, 2):
            password_keyboard.append(InlineKeyboardButton("", callback_data=""))
            password_keyboard.append(InlineKeyboardButton("", callback_data=""))

        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def select_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        option = query.data

        keyboard = [
            [InlineKeyboardButton("", callback_data="")],
            [InlineKeyboardButton("", callback_data="")]
        ]

        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def select_option(self, update: Update, context: CallbackContext):
        return MyPasswordState.EDIT_RETRIEVE_PASSWORD

    def edit_retrieve_password(self, update: Update, context: CallbackContext):
        return MyPasswordState.SELECT_PASSWORD

    def cancel(self, update: Update, context: CallbackContext):
        return MyPasswordState.SELECT_PASSWORD

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("mypasswords", self.start)],
            states={
                MyPasswordState.SELECT_PASSWORD: [CallbackQueryHandler(self.select_password)],
                MyPasswordState.SELECT_PASSWORD_OPTIONS: [CallbackQueryHandler(self.select_option)],
                MyPasswordState.EDIT_RETRIEVE_PASSWORD: [CallbackQueryHandler(self.edit_retrieve_password)]
            },
            fallbacks=[
                CommandHandler("mypasswords", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )

        self.set_conversation(conversation)
