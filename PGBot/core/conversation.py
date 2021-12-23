from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from abc import ABCMeta, abstractmethod
from typing import Union

class BaseConversation(metaclass=ABCMeta):
    def __init__(self):
        self._conversation = None

    def set_conversation(self, conversation: ConversationHandler):
        self._conversation = conversation

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

