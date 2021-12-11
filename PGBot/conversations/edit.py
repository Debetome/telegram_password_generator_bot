from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

from PGBot.core.conversation import BaseConversation
from PGBot.core.logger import logger

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.cryptoHandler import CryptoHandler

from PGBot.states import EditState

class EditConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler
        self.register = None
        self.newValue = None

    def start(self, update: Update, context: CallbackContext):
        passwords = dbHandler.get_passwords(int(update.message.chat_id))
        passwords_keyboard = []

        for i, item in enumerate(
        return EditState.SELECT_PASSWORD

    def select_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.register = dbHandler.get_password(int(query.data))

        options_keyboard = [
            [InlineKeyboardButton("Edit password", callback_data=str(1))],
            [InlineKeyboardButton("Edit title", callback_data=str(2))]
        ]

        markup = InlineKeyboardMarkup(options_keyboard)
        update.message.reply_text("", reply_markup=markup)
        return EditState.SELECT_OPTION

    def select_option(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        return EditState.RETRIEVE_VALUE

    def retrieve_password(self, update: Update, context: CallbackContext):
        return None

    def retrieve_title(self, update: Update, context: CallbackContext):
        return None

    def retrieve_value(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        return EditState.SELECT_PASSWORD

    def cancel(self, update: Update, context: CallbackContext):
        update.message.reply_text("Edit password operation cancelled!")
        return EditState.SELECT_PASSWORD

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("edit", self.start)],
            states={
                EditState.SELECT_PASSWORD: [CallbackQueryHandler(self.select_password)],
                EditState.SELECT_OPTION: [
                ]
            },
            fallbacks=[
                CommandHandler("edit", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )

        self.set_conversation(conversation)
