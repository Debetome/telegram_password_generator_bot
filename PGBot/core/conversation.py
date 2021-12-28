from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Union, Callable

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


class BaseConversation(metaclass=ABCMeta):
    def __init__(self, bot: object):
        self.bot = bot
        self._conversation = None
        self._state = 0

    def set_state_on(self):
        self.bot.set_last_conversation(self)
        self._state = 1

    def set_state_off(self):
        self.bot.set_last_conversation(self)
        self._state = 0

    def set_conversation(self, conversation: ConversationHandler):
        if not isinstance(conversation, ConversationHandler):
            return None
        self._conversation = conversation

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
    def operation(self) -> str:
        pass

    @abstractmethod
    def cancel_state(self) -> object:
        pass

    @abstractmethod
    def setup(self):
        pass

