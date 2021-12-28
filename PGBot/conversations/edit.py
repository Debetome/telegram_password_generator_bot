from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
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
from PGBot.handlers.encryptHandler import EncryptHandler

from PGBot.constants import EditState

class EditConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler
        self.register = None
        self.choice = 0

    def start(self, update: Update, context: CallbackContext):
        passwords = self.dbHandler.get_passwords(int(update.message.chat_id))
        passwords_keyboard = []

        if len(passwords) == 0:
            update.message.reply_text("You haven't stored any password yet!")
            return EditState.SELECT_PASSWORD

        for i in range(0, len(passwords), 2):
            stack = []
            if abs(i-len(passwords)) != 1:
                stack.extend([
                    InlineKeyboardButton(passwords[i].title, callback_data=passwords[i].id),
                    InlineKeyboardButton(passwords[i+1].title, callback_data=passwords[i+1].id)
                ])
            else:
                stack.append(InlineKeyboardButton(passwords[i][0], callback_data=passwords[i][0].id))

            passwords_keyboard.append(stack)

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

    def edit_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text("Send the new password ...")
        self.choice = 1
        return EditState.RETRIEVE_VALUE

    def edit_title(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text("Send the new title you'll be refering to this password ...")
        self.choice = 2
        return EditState.RETRIEVE_VALUE

    def retrieve_value(self, update: Update, context: CallbackContext):
        value = update.message.text

        if self.choice == 1:
            self.register.password = value
        elif self.choice == 2:
            self.register.title = value

        self.dbHandler.update_password(self.register)
        return EditState.SELECT_PASSWORD

    @property
    def operation(self):
        return "Edit password"

    @property
    def cancel_state(self) -> EditState:
        return EditState.SELECT_PASSWORD

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("edit", self.start)],
            states={
                EditState.SELECT_PASSWORD: [CallbackQueryHandler(self.select_password)],
                EditState.RETRIEVE_VALUE: [MessageHandler(Filters.text & ~Filters.command, self.retrieve_value)]
            },
            fallbacks=[
                CommandHandler("edit", self.start),
                CommandHandler("cancel", self.bot.cancel)
            ]
        )

        self.set_conversation(conversation)
