"""Repository abstractions for managing users."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, Optional

from .models import User


class UserAlreadyExists(Exception):
    """Raised when attempting to create a user that already exists."""


class UserNotFound(Exception):
    """Raised when requesting a user that does not exist."""


class InMemoryUserRepository:
    """A simple in-memory repository suitable for demos and testing."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def add(self, user: User) -> None:
        if user.id in self._users:
            raise UserAlreadyExists(f"User '{user.id}' already exists")
        self._users[user.id] = user

    def get(self, user_id: str) -> User:
        try:
            return self._users[user_id]
        except KeyError as error:
            raise UserNotFound(f"User '{user_id}' was not found") from error

    def update(self, user: User) -> None:
        if user.id not in self._users:
            raise UserNotFound(f"User '{user.id}' was not found")
        self._users[user.id] = user

    def exists(self, user_id: str) -> bool:
        return user_id in self._users

    def all(self) -> Iterable[User]:
        return list(self._users.values())

    def clear(self) -> None:
        self._users.clear()
