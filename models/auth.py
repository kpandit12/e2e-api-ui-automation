"""Auth-related Pydantic models."""

from pydantic import BaseModel, Field


class Authentication(BaseModel):
    """The nested ``authentication`` object in a Juice Shop login response."""

    token: str = Field(..., min_length=1)
    bid: int | None = None
    umail: str | None = None


class LoginResponse(BaseModel):
    """Response body of ``POST /rest/user/login`` on success."""

    authentication: Authentication
