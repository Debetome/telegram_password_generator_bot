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
from PGBot.core.states import *
from PGBot.core.strings import *

from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.cryptoHandler import CryptoHandler

from PGBot.models import Password


class PasswordGeneratorBot:
    def __init__(self, token: str, database: str, logfile: str):
        self.token = token
        self.database = database
        self.logfile = logfile

        self.updater = None
        self.distpacher = None
        self.dbHandler = None
        self.cryptoHandler = None

        self.password = None
        self.passwordRegister = None

    def _generate_password(self) -> str:
        return "".join(choices(self.password.chars, k=self.password.length))

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Start message!")

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Help message!")

    def generate(self, update: Update, context: CallbackContext):
        self.password = Password()
        keyboard = [
            [InlineKeyboardButton(LOWER_UPPER, callback_data=LOWER_UPPER)],
            [InlineKeyboardButton(LOWER_DIGITS, callback_data=LOWER_DIGITS)],
            [InlineKeyboardButton(UPPER_DIGITS, callback_data=UPPER_DIGITS)],
            [InlineKeyboardButton(LOWER_UPPER_DIGITS, callback_data=LOWER_UPPER_DIGITS)],
            [InlineKeyboardButton(ALL, callback_data=ALL)],
            [InlineKeyboardButton(ONLY_DIGITS, callback_data=ONLY_DIGITS)]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("What characters would you like your password to have?", reply_markup=markup)
        return GenerateState.SELECT_CHARS

    def select_chars(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        self.password.chars = query.data

        query.edit_message_text("Type the password length ...")
        return GenerateState.SELECT_LENGTH

    def select_length(self, update: Update, context: CallbackContext):
        message = update.message.text
        length = [a for a in [b for b in message if b in digits]]

        if len(length) == 0:
            update.message.reply_text("Invalid password length!")
            return ConversationHandler.END

        self.password.length = int("".join(length))
        self._send_password(update.message.chat_id)
        return ConversationHandler.END

    def _send_password(self, chat_id):
        bot = self.updater.bot
        password = self._generate_password()
        self.password = None
        return bot.send_message(
            chat_id=chat_id,
            text=f"{password}"
        )

    def save(self, update: Update, context: CallbackContext):
        self.passwordRegister = PasswordRegister()
        update.message.reply_text("Send password to save")
        return SaveState.RETRIEVE_PASS

    def retrieve_passw(self, update: Update, context: CallbackContext):
        self.passwordRegister.password = update.message.text
        update.message.reply_text("Set a title for this password")
        return SaveState.RETRIVE_TITLE

    def retrieve_title(self, update: Update, context: CallbackContext):
        self.passwordRegister.title = update.message.text
        self.passwordRegister.chat_id = update.message.chat_id
        self._save_password()

        update.message.reply_text("Password saved!")
        return ConversationHandler.END

    def _save_password(self):
        password = self.passwordRegister
        dbHandler.insert_password(password)

    def my_passwords(self, update: Update, context: CallbackContext):
        passwords = dbHandler.get_passwords(int(update.message.chat_id))
        keyboard = []

        if len(passwords) == 0:
            update.message.reply_text("You haven't stored passwords here yet!")
            return ConversationHandler.END

        for i in range(0, len(passwords), 2):
            stack = []
            if abs(i-len(passwords)) != 1:
                stack.append(InlineKeyboardButton(passwords[i][0], callback_data=passwords[i][1]))
                stack.append(InlineKeyboardButton(passwords[i+1][0], callback_data=passwords[i+1][1]))
            else:
                stack.append(InlineKeyboardButton(passwords[i][0]))

            keyboard.append(stack)

        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🔑 Your passwords", reply_markup=markup)
        return MyPasswordState.SELECT_PASSWORD

    def select_password(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        chosen_password = query.data
        chat_id = query.message.chat_id
        user_id = query.message.from_user["id"]

        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=1),
                InlineKeyboardButton("", callback_data=2)
            ],

        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def select_password_options(self, update: Update, context: CallbackContext):
        return None

    def delete(self, update: Update, context: CallbackContext):
        pass

    def cancel(self, update: Update, context: CallbackContext):
        return ConversationHandler.END

    def run(self):
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dbHandler = DatabaseHandler(self.database)
        self.cryptoHandler = CryptoHandler()

        gen_passwd_conversation = ConversationHandler(
            entry_points=[CommandHandler("generate", self.generate)],
            states={
                GenerateState.SELECT_CHARS: [CallbackQueryHandler(self.select_chars)],
                GenerateState.SELECT_LENGTH: [MessageHandler(Filters.text, self.select_length)]
            },
            fallbacks=[
                CommandHandler("start", self.start),
                CommandHandler("help", self.help),
                CommandHandler("generate", self.generate),
                CommandHandler("save", self.save)
            ]
        )

        save_passw_conversation = ConversationHandler(
            entry_points=[CommandHandler("save", self.save)],
            states={
                SaveState.RETRIEVE_PASS: [MessageHandler(Filters.text & ~Filters.command, self.retrieve_passw)],
                SaveState.RETRIEVE_TITLE: [MessageHandler(Filters.text & ~Filters.command, self.retrieve_title)]
            },
            fallbacks=[
                CommandHandler("start", self.start),
                CommandHandler("help", self.help),
                CommandHandler("generate", self.generate),
                CommandHandler("save", self.save)
            ]
        )

        my_passwords_conversation = ConversationHandler(
            entry_points=[CommandHandler("mypasswords", self.my_passwords)],
            states={
                MyPasswordState.SELECT_PASSWORD: [CommandHandler("mypasswords", self.select_password)]
            },
            fallbacks=[
                CommandHandler("start", self.start),
                CommandHandler("help", self.help),
                CommandHandler("generate", self.generate),
                CommandHandler("save", self.save)
            ]
        )

        delete_password_conversation = ConversationHandler(
            entry_points=[CommandHandler("delete", self.delete)],
            states={
                DeletePassword.SELECT_PASSWORD: [CommandHandler("delete", self.delete)]
            },
            fallbacks=[
                CommandHandler("start", self.start),
                CommandHandler("help", self.help),
                CommandHandler("generate", self.generate),
                CommandHandler("save", self.save)
            ]
        )

        self.dispatcher.add_handler(gen_passw_conversation)
        self.dispatcher.add_handler(save_passw_conversation)
        self.dispatcher.add_handler(my_passwords_conversation)
        
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))

        self.updater.start_polling()
        self.updater.idle()
