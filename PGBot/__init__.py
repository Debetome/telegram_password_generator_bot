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

from PGBot.core.logger import logger
from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.encryptHandler import EncryptHandler

from PGBot.conversations.generate import GenerateConversation
from PGBot.conversations.edit import EditConversation
from PGBot.conversations.save import SaveConversation
from PGBot.conversations.mypasswords import MyPasswordsConversation
from PGBot.conversations.export import ExportConversation
from PGBot.conversations.delete import DeleteConversation

from PGBot.models import Password
from PGBot.tables import TABLES
from PGBot.constants import *


class PasswordGeneratorBot:
    def __init__(self, token: str, database: str, logfile: str):
        self.token = token
        self.database = database
        self.logfile = logfile

        self.updater = None
        self.distpacher = None
        self.dbHandler = None
        self.encryptHandler = None

        self.conversations = []
        self.last_conversation = None

    def start(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        update.message.reply_text("Start message!")
        logger.info(f"{' '.join(user)} used command 'start'")

    def help(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        update.message.reply_text("Help message!")
        logger.info(f"{' '.join(user)} used command 'help'")

    def about(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        update.message.reply_text("About command!")
        logger.info(f"{' '.join(user)} used command 'about'")

    def _define_conversations(self):
        self.conversations.extend([
            GenerateConversation(self.dbHandler),
            EditConversation(self.dbHandler),
            SaveConversation(self.dbHandler),
            MyPasswordsConversation(self.dbHandler),
            DeleteConversation(self.dbHandler)
        ])

    def _setup_conversations(self):
        for conv in self.conversations:
            conv.setup()

    def _set_conversations(self):
        for conv in self.conversations:
            self.dispatcher.add_handler(conv.conversation)

    def _set_basic_commands(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("about", self.about))

    def set_last_conversation(self, conv: BaseConversation):
        self.last_conversation = conv

    def run(self):
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dbHandler = DatabaseHandler(self.database)
        self.encryptHandler = EncryptHandler()

        self._define_conversations()
        self._setup_conversations()
        self._set_conversations()
        self._set_basic_commands()

        self.dbHandler.create_database()
        self.updater.start_polling()
        self.updater.idle()
