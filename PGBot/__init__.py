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

from PGBot.conversations.generate import GenerateConversation
from PGBot.conversations.edit import EditConversation
from PGBot.conversations.save import SaveConversation
from PGBot.conversations.mypasswords import MyPasswordsConversation
from PGBot.conversations.delete import DeleteConversation

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

        self.conversations = []

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Start message!")

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Help message!")

    def about(self, update: Update, context: CallbackContext):
        update.message.reply_text("About command!")

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
            return GenerateState.SELECT_CHARS

        self.password.length = int("".join(length))
        self._send_password(update.message.chat_id)
        return GenerateState.SELECT_CHARS

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
        return SaveState.RETRIEVE_TITLE

    def retrieve_title(self, update: Update, context: CallbackContext):
        self.passwordRegister.title = update.message.text
        self.passwordRegister.chat_id = update.message.chat_id
        self._save_password()

        update.message.reply_text("Password saved!")
        return SaveState.RETRIEVE_PASS

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
                InlineKeyboardButton("Edit", callback_data=str(1)),
                InlineKeyboardButton("Delete", callback_data=str(2)),
                InlineKeyboardButton("<< Back", callback_data=str(3))
            ]
        ]

        query.edit_message_text(text="", reply_markup=keyboard)
        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def mypasswords_edit(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        keyboard = [
            [InlineKeyboardButton("Yes", callback_data="yes")],
            [InlineKeyboardButton("No", callback_data="no")]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Are you sure you want to edit this password?", reply_markup=markup)
        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def mypasswords_edit_option(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        choice = query.data

        if choice == "yes":
            query.edit_message_text("Send the new password ...")
            return MyPasswordState.EDIT_RETRIEVE_PASSWORD

        elif choice == "no":
            query.edit_message_text("Operation cancelled!")
            return MyPasswordState.SELECT_PASSWORD

    def mypasswords_edit_retrieve_password(self, update: Update, context: CallbackContext):
        password = update.message.text
        update.message.reply_text("Password changed!")
        return MyPasswordState.SELECT_PASSWORD

    def mypasswords_delete(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        keyboard = [
            [InlineKeyboardButton("Yes", callback_data="yes")],
            [InlineKeyboardButton("No", callback_data="no")]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Are you sure you want to delete this password?", reply_markup=markup)
        return MyPasswordState.SELECT_PASSWORD_OPTIONS

    def mypasswords_delete_option(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        choice = query.data

        if choice == "yes":
            query.edit_message_text("Password deleted")
            return MyPasswordState.SELECT_PASSWORD
        elif choice == "no":
            query.edit_message_text("Operation cancelled")
            return MyPasswordState.SELECT_PASSWORD

    def _setup_conversations(self):
        self.conversations.extend([
            GenerateConversation(self.dbHandler),
            EditConversation(self.dbHandler),
            SaveConversation(self.dbHandler),
            MyPasswordsConversation(self.dbHandler),
            DeleteConversation(self.dbHandler)
        ])

        for conv in self.conversations:
            conv.setup()

    def _set_conversations(self):
        for conv in self.conversations:
            self.dispatcher.add_handler(conv.conversation)

    def _set_basic_commands(self):
        self.dispatcher(CommandHandler("start", self.start))
        self.dispatcher(CommandHandler("help", self.help))
        self.dispatcher(CommandHandler("about", self.about))

    def run(self):
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dbHandler = DatabaseHandler(self.database)
        self.cryptoHandler = CryptoHandler()

        self._setup_conversations()
        self._set_conversations()
        self._set_basic_commands()

        self.updater.start_polling()
        self.updater.idle()
