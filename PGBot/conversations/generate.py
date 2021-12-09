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

from random import choices

from PGBot.core.logger import logger
from PGBot.core.conversation import BaseConversation
from PGBot.core.strings import *

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.cryptoHandler import CryptoHandler

from PGBot.states import GenerateState
from PGBot.models import Password

class GenerateConversation(BaseConversation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._password = None
        self._password_obj = None

    def _generate_password(self):
        if self._password_obj is not None:
            return None

        chars = self._password_obj.chars
        length = self._password_obj.length
        return "".join(choices(chars, k=length))

    def start(self, update: Update, context: CallbackContext):
        self._password_obj = Password()
        keyboard = [
            [InlineKeyboardButton(LOWER_UPPER, callback_data=LOWER_UPPER)],
            [InlineKeyboardButton(LOWER_DIGITS, callback_data=LOWER_DIGITS)],
            [InlineKeyboardButton(LOWER_UPPER_DIGITS, callback_data=LOWER_UPPER_DIGITS)],
            [InlineKeyboardButton(ALL, callback_data=ALL)],
            [InlineKeyboardButton(ONLY_DIGITS, callback_data=ONLY_DIGITS)]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("", reply_markup=markup)
        return GenerateState.SELECT_CHARS

    def select_chars(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self._password_obj.chars = query.data

        query.edit_message_text("Type the password length ...")
        return GenerateState.SELECT_LENGTH

    def select_length(self, update: Update, context: CallbackContext):
        message = update.message.text
        length = [a for a in [b for b in message if b in digits]]

        if len(length) == 0:
            update.message.reply_text("Invalid password length!")
            return GenerateState.SELECT_LENGTH

        self._password_obj.length = int("".join(length))

        keyboard = [
            [InlineKeyboardButton("Save", callback_data=1)],
            [InlineKeyboardButton("Don't save", callback_data=0)]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        password = self._generate_password()
        self._password_obj = None
        update.message.reply_text(
            text=password,
            reply_markup=markup
        )
        return GenerateState.SAVE_PASSWORD

    def save_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=self._password)

        choice = query.data
        bot = query.bot

        if choice == 1:
            bot.send_message(
                chat_id=query.message.chat_id,
                text="Password saved!"
            )

        return GenerateState.SELECT_CHARS

    def cancel(self, update: Update, context: CallbackContext):
        update.message.edit_text("Operation cancelled!")
        return GenerateState.SELECT_CHARS

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("generate", self.start)],
            states={
                GenerateState.SELECT_CHARS: [CallbackQueryHandler(self.select_chars)],
                GenerateState.SELECT_LENGTH: [CallbackQueryHandler(self.select_length)],
                GenerateState.SAVE_PASSWORD: [CallbackQueryHandler(self.save_password)]
            },
            fallbacks=[
                CommandHandler("generate", self.start),
                CommandHandler("cancel", self.cancel)
            ]
        )
        self.set_conversation(conversation)
