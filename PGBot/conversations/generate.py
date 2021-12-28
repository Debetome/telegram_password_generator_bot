from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

from random import choices

from PGBot.core.logger import logger
from PGBot.core.conversation import *
from PGBot.handlers.dbHandler import DatabaseHandler
from PGBot.handlers.encryptHandler import EncryptHandler

from PGBot.constants import GenerateState
from PGBot.constants import Characters
from PGBot.models import User
from PGBot.models import Password
from PGBot.models import PasswordRegister

class GenerateConversation(BaseConversation):
    def __init__(self, dbHandler: DatabaseHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbHandler = dbHandler
        self.password_obj = None
        self.password = None
        self.email = None

    def _generate_password(self):
        if self.password_obj is None:
            return None

        chars = self.password_obj.chars
        length = self.password_obj.length
        return "".join(choices(chars, k=length))

    def start(self, update: Update, context: CallbackContext):
        self.set_state_on()

        self.password_obj = Password()
        self.register = PasswordRegister()

        keyboard = [
            [InlineKeyboardButton(Characters.LOWER_UPPER, callback_data=Characters.LOWER_UPPER)],
            [InlineKeyboardButton(Characters.LOWER_DIGITS, callback_data=Characters.LOWER_DIGITS)],
            [InlineKeyboardButton(Characters.UPPER_DIGITS, callback_data=Characters.UPPER_DIGITS)],
            [InlineKeyboardButton(Characters.LOWER_UPPER_DIGITS, callback_data=Characters.LOWER_UPPER_DIGITS)],
            [InlineKeyboardButton(Characters.ALL, callback_data=Characters.ALL)],
            [InlineKeyboardButton(Characters.ONLY_DIGITS, callback_data=Characters.ONLY_DIGITS)]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("What characters do you wish your password to have?", reply_markup=markup)
        return GenerateState.SELECT_CHARS

    def select_chars(self, update: Update, context: CallbackContext):
        self.set_state_on()
        query = update.callback_query
        self.chars_query = query
        bot = query.bot
        query.answer()

        if query.data == '1': 
            query.edit_message_text(text=f"{self.password}")
            bot.send_message(
                text="🔤 Set a name for this password ...",
                chat_id=int(query.message.chat_id)
            )
            return GenerateState.SAVE_PASSWORD

        elif query.data == '2':
            query.edit_message_text(
                text=f"{self.password}",
            )
            return GenerateState.SELECT_CHARS

        elif query.data == '3':
            bot.send_message(
                text="📨 Type the email to send this password to ...",
                chat_id=int(query.message.chat_id)
            )
            return GenerateState.SEND_EMAIL

        self.password_obj.chars = query.data
        self.password_obj.message_id = query.message.message_id

        query.edit_message_text("📏 Set a password length ...")
        return GenerateState.SELECT_LENGTH

    def select_length(self, update: Update, context: CallbackContext):
        self.set_state_on()
        bot = context.bot
        message = update.message.text
        length = "".join([b for b in message if b in Characters.ONLY_DIGITS])

        if len(length) == 0:
            update.message.reply_text("Invalid password length!")
            return GenerateState.SELECT_LENGTH

        if int(length) < 8:
            update.message.reply_text("Password length too short!")
            return GenerateState.SELECT_LENGTH
        elif int(length) > 256 and int(length) < 500:
            update.message.reply_text("Password length too long!")
            return GenerateState.SELECT_LENGTH
        
        if int(length) > 500:
            update.message.reply_text("Password EXCESSIVELY long!")
            return GenerateState.SELECT_LENGTH

        self.password_obj.length = int(length)

        keyboard = [
            [
                InlineKeyboardButton("💾 Save", callback_data=str(1)),
                InlineKeyboardButton("🚫 NOT save", callback_data=str(2))
            ],
            [InlineKeyboardButton("✉ Send to email", callback_data=str(3))]
        ]

        markup = InlineKeyboardMarkup(keyboard)
        self.password = self._generate_password()

        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"{self.password}",
            reply_markup=markup
        )

        self.password_obj = Password()
        return GenerateState.SAVE_PASSWORD

    def save_password(self, update: Update, context: CallbackContext):
        self.set_state_on()
        query = update.callback_query
        query.answer()

        query.edit_message_text(text=f"{self.password}")

        bot = query.bot
        bot.send_message(
            text="🔤 Set a name for this password ...",
            chat_id=int(query.message.chat_id)
        )

        return GenerateState.SAVE_PASSWORD

    def not_save_password(self, update: Update, context: CallbackContext):
        self.set_state_on()
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f"{self.password}")
        return GenerateState.SELECT_CHARS

    def retrieve_title(self, update: Update, context: CallbackContext):
        self.set_state_on()
        title = update.message.text
        chat_id = int(update.message.chat_id)

        def user_generator() -> User:
            for user in self.dbHandler.get_users():
                yield user

        user = [u for u in user_generator() if u.chat_id == chat_id]

        if len(user) == 0:
            firstname = update.message.from_user.first_name
            lastname = update.message.from_user.last_name

            self.dbHandler.insert_user(User(
                firstname=firstname,
                lastname=lastname,
                chat_id=chat_id
            ))

            user = [u for u in user_generator() if u.chat_id == chat_id][0]

        else:
            user = user[0]

        self.dbHandler.insert_password(PasswordRegister(
            title=title,
            password=self.password,
            user_id=user.id
        ))

        update.message.reply_text("✅ Password saved succesfuly!")
        return GenerateState.SELECT_CHARS

    def send_email(self, update: Update, context: CallbackContext):
        self.set_state_on()
        bot = update.bot
        update.message.reply_text(
            text="📨 Type the email to send this password to ...",
        )
        return GenerateState.SELECT_CHARS

    def retrieve_email(self, update: Update, context: CallbackContext):
        self.email = update.message.text
        return None

    @property
    def operation(self) -> str:
        return "Generate password"

    @property
    def cancel_state(self) -> GenerateState:
        return GenerateState.SELECT_CHARS

    def setup(self):
        conversation = ConversationHandler(
            entry_points=[CommandHandler("generate", self.start)],
            states={
                GenerateState.SELECT_CHARS: [CallbackQueryHandler(self.select_chars)],
                GenerateState.SELECT_LENGTH: [
                    MessageHandler(filters=Filters.text & ~Filters.command, callback=self.select_length)
                ],
                GenerateState.SAVE_PASSWORD: [
                    CallbackQueryHandler(pattern="^1$", callback=self.save_password),
                    CallbackQueryHandler(pattern="^2$", callback=self.not_save_password),
                    CallbackQueryHandler(pattern="^3$", callback=self.send_email),
                    MessageHandler(Filters.text & ~Filters.command, self.retrieve_title)
                ],
                GenerateState.SEND_EMAIL: [
                    MessageHandler(Filters.text & ~Filters.command, self.send_email)
                ]
            },
            fallbacks=[
                CommandHandler("generate", self.start),
                CommandHandler("cancel", self.bot.cancel)
            ]
        )
        self.set_conversation(conversation)
