from dataclasses import dataclass, field

@dataclass
class User:
    id: int = field(default_factory=int)
    firstname: str = field(default_factory=str)
    lastname: str = field(default_factory=str)
    chat_id: int = field(default_factory=int)

@dataclass
class PasswordRegister:
    id: int = field(default_factory=int)
    title: str = field(default_factory=str)
    password: str = field(default_factory=str)
    chat_id: int = field(default_factory=int)

@dataclass
class Password:
    chars: str = field(default_factory=str)
    length: int = field(default_factory=int)
