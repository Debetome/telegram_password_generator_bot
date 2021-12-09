from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler
)

from PGBot.core.conversation import BaseConversation
from PGBot.core.logger import logger
from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.states import DeletePassword

class DeleteConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler

    def start(self, update: Update, context: CallbackContext):
        return DeletePassword.SELECT_PASSWORD

    def select_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        password = query.data

        keyboard = [
            [InlineKeyboardButton("Yes", callback_data=1)],
            [InlineKeyboardButton("No", callback_data=0)]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text="Are you sure you want to delete this password?",
            reply_markup=markup
        )
        return DeletePassword.CONFIRM_DELETION

    def confirm_deletion(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        choice = query.data

        if choice == 1:
            query.edit_message_text("Password not deleted!")
        elif choice == 0:
            query.edit_message_text("Password deleted!")

        return DeletePassword.SELECT_PASSWORD

    def cancel(self, update: Update, context: CallbackContext):
        update.message.edit_text("Operation cancelled!")
        return DeletePassword.SELECT_PASSWORD

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("delete", self.start)],
            states={
                DeletePassword.SELECT_PASSWORD: [CallbackQueryHandler(self.select_password)]
            },
            fallbacks=[
                CommandHandler("delete", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )

        self.set_conversation(conversation)
