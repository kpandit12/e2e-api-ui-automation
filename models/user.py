"""User-related Pydantic models."""

from typing import Any

from pydantic import BaseModel, Field


class User(BaseModel):
    """A Juice Shop user account, as returned by ``GET /rest/user/whoami``."""

    id: int | None = None
    email: str
    role: str | None = None


class NewUser(BaseModel):
    """Payload for registering a new user via ``POST /api/Users/``."""

    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=5)
    passwordRepeat: str = Field(..., min_length=5)
    securityQuestion: dict[str, Any] | None = None
    securityAnswer: str | None = None
