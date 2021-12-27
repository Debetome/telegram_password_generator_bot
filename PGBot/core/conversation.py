from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from abc import ABCMeta, abstractmethod
from typing import Union, Callable
from functools import wraps

def cancel_command(func: Callable):
    @wraps(func)
    def wrapper(*args):
        conv = args[0]
        update = args[1]

        if conv.state != 1:
            update.message.reply_text("No operation running!")
            return None

        conv.set_state_off()
        func(*args)

    return wrapper

class BaseConversation(metaclass=ABCMeta):
    def __init__(self, bot: object):
        self._bot = bot
        self._conversation = None
        self._state = 0

    def set_conversation(self, conversation: ConversationHandler):
        self._conversation = conversation

    def set_state_on(self):
        self._state = 1

    def set_state_off(self):
        self._state = 0

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def state(self) -> int:
        return self._state

    @property
    def conversation(self) -> Union[ConversationHandler, None]:
        if self._conversation is None:
            return None
        return self._conversation

    @abstractmethod
    def start(self, update: Update, context: CallbackContext):
        pass

    @abstractmethod
    def cancel(self, update: Update, context: CallbackContext):
        pass

    @abstractmethod
    def setup(self):
        pass

