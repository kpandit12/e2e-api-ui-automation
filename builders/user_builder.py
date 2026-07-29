"""Fluent builder for test user accounts.

``with_unique_email()`` bakes a uuid into the local-part so parallel test
workers (pytest-xdist) never collide on the same email.
"""
from __future__ import annotations

import uuid

from models.user import NewUser

DEFAULT_PASSWORD = "Automation123!"


class UserBuilder:
    """Builds a :class:`NewUser` payload, defaulting to a unique account."""

    def __init__(self) -> None:
        self._email = f"qa+{uuid.uuid4().hex[:12]}@automation.test"
        self._password = DEFAULT_PASSWORD
        self._password_repeat: str | None = None

    def with_email(self, email: str) -> UserBuilder:
        self._email = email
        return self

    def with_unique_email(self, prefix: str = "qa") -> UserBuilder:
        self._email = f"{prefix}+{uuid.uuid4().hex[:12]}@automation.test"
        return self

    def with_password(self, password: str) -> UserBuilder:
        self._password = password
        return self

    def with_mismatched_repeat(self, repeat: str) -> UserBuilder:
        """Force ``passwordRepeat`` to diverge, for negative registration tests."""
        self._password_repeat = repeat
        return self

    def build(self) -> NewUser:
        return NewUser(
            email=self._email,
            password=self._password,
            passwordRepeat=self._password_repeat or self._password,
        )
