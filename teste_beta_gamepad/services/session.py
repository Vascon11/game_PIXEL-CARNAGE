# services/session.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Session:
    user_id: str
    email: str
    username: str
    best_wave: int = 0

_current: Optional[Session] = None

def set_session(user_id: str, email: str, username: str) -> None:
    global _current
    _current = Session(user_id=user_id, email=email, username=username, best_wave=0)

def clear_session() -> None:
    global _current
    _current = None

def get_session() -> Optional[Session]:
    return _current

def is_logged_in() -> bool:
    return _current is not None

def set_best_wave(value: int) -> None:
    if _current:
        _current.best_wave = int(value)