from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

from typing import List 

from PGBot.core.conversation import BaseConversation
from PGBot.core.logger import logger

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.encryptHandler import EncryptHandler

from PGBot.constants import MyPasswordState
from PGBot.models import PasswordRegister

class MyPasswordsConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler
        self.register = None

    def _get_passwords(self, chat_id: int) -> List[PasswordRegister]:
        passwords = self.dbHandler.get_passwords(chat_id)
        for i in range(0, passwords, 2):
            stack = []
            if abs(i-len(passwords)) != 1:
                stack.extend([
                    InlineKeyboardButton(passwords[i].title, callback_data=passwords[i].id),
                    InlineKeyboardButton(passwords[i+1].title, callback_data=passwords[i+1].id)
                ])
            else:
                stack.append(InlineKeyboardButton(passwords[i].title, callback_data=passwords[i].id))

            yield stack

    def start(self, update: Update, context: CallbackContext):
        chat_id = int(update.message.chat_id)
        passwords_keyboard = [p for p in self._get_passwords(chat_id)]
        markup = InlineKeyboardMarkup(passwords_keyboard)
        update.message.reply_text("Your passwords", reply_markup=markup)
        return MyPasswordState.SELECT_PASSWORD

    def start_over(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        chat_id = int(update.message.chat_id)
        passwords_keyboard = [p for p in self._get_passwords(chat_id)]
        markup = InlineKeyboardMarkup(passwords_keyboard)
        update.message.reply_text("Your passwords", reply_markup=markup)
        return MyPasswordState.SELECT_PASSWORD

    def select_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.register = self.dbHandler.get_password(int(query.data))

        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=str(2)),
                InlineKeyboardButton("Delete", callback_data=str(3))
            ],
            [InlineKeyboardButton("Back to selection", callback_data=str(4))]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"{self.register.password}", 
            reply_markup=markup
        )

        return MyPasswordState.SELECT_PASSWORD

    def edit_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
    
        keyboard = [
            [
                InlineKeyboardButton("Edit title", callback_data=str(1)),
                InlineKeyboardButton("Edit password", callback_data=str(2))
            ],
            [InlineKeyboardButton("Back to options", callback_data=str(3))]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"Title: {self.register.title}\nPassword: {self.register.password}", 
            reply_markup=markup
        )

        return MyPasswordState.EDIT_PASSWORD

    def edit_retrieve_title(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.option = "title"
        return MyPasswordState.EDIT_RETRIEVE_VALUE

    def edit_retrieve_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.option = "password"
        return MyPasswordState.EDIT_RETRIEVE_VALUE

    def edit_retrieve_value(self, update: Update, context: CallbackContext):
        value = update.message.text
        setattr(self.register, self.option, value)
        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def delete_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=str(1)),
                InlineKeyboardButton("No", callback_data=str(2))
            ],
        ]

        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Are you sure you want to delete this password?",
            reply_markup=markup
        )

        return MyPasswordState.DELETE_PASSWORD

    def confirm_deletion(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.dbHandler.delete_password(self.register)
        return MyPasswordState.SELECT_PASSWORD

    @property
    def operation(self) -> str:
        return "My passwords"

    @property
    def cancel_state(self) -> MyPasswordState:
        return MyPasswordState.SELECT_PASSWORD

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("mypasswords", self.start)],
            states={
                MyPasswordState.SELECT_PASSWORD: [
                    CallbackQueryHandler(pattern="^1$", callback=self.select_password),
                    CallbackQueryHandler(pattern="^2$", callback=self.edit_password),
                    CallbackQueryHandler(pattern="^3$", callback=self.delete_password),
                    CallbackQueryHandler(pattern="^4$", callback=self.start_over)
                ],
                MyPasswordState.EDIT_PASSWORD: [
                    CallbackQueryHandler(pattern="^1$", callback=self.edit_retrieve_title),
                    CallbackQueryHandler(pattern="^2$", callback=self.edit_retrieve_password),
                    CallbackQueryHandler(pattern="^3$", callback=self.select_password)
                ],
                MyPasswordState.EDIT_RETRIEVE_VALUE: [
                    MessageHandler(filters=Filters.text & ~Filters.command, callback=self.edit_retrieve_value)
                ],
                MyPasswordState.DELETE_PASSWORD: [
                    CallbackQueryHandler(pattern="^1$", callback=self.confirm_deletion),
                    CallbackQueryHandler(pattern="^2$", callback=self.select_password)
                ]
            },
            fallbacks=[
                CommandHandler("mypasswords", self.start),
                CommandHandler("cancel", self.bot.cancel)
            ]
        )

        self.set_conversation(conversation)
