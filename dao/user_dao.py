"""DAO for user-account endpoints (``/api/Users``, ``/rest/user/whoami``)."""
from __future__ import annotations

from clients.rest_client import ApiResponse, RestClient
from core.exceptions import ApiError
from models.user import User


def register_response(
    client: RestClient,
    email: str,
    password: str,
    *,
    password_repeat: str | None = None,
) -> ApiResponse:
    """``POST /api/Users/`` returning the raw response (for negative tests)."""
    return client.post(
        "/api/Users/",
        json={
            "email": email,
            "password": password,
            "passwordRepeat": password_repeat or password,
        },
    )


def register(
    client: RestClient,
    email: str,
    password: str,
    *,
    password_repeat: str | None = None,
) -> int:
    """``POST /api/Users/`` -> the new user's id.

    Raises:
        ApiError: If registration is rejected (e.g. duplicate email).
    """
    response = register_response(
        client, email, password, password_repeat=password_repeat
    )
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
    return int(response.json["data"]["id"])


def whoami_response(client: RestClient) -> ApiResponse:
    """``GET /rest/user/whoami`` returning the raw response.

    Juice Shop authenticates this endpoint via the ``token`` cookie (set
    automatically by :meth:`RestClient.set_token`), not the ``Authorization``
    header, so this deliberately does not pass ``authenticated=True``.
    """
    return client.get("/rest/user/whoami")


def whoami(client: RestClient) -> User:
    """``GET /rest/user/whoami`` -> the authenticated user.

    Raises:
        ApiError: If the token is missing/invalid or no user is logged in.
    """
    response = whoami_response(client)
    body = response.json or {}
    if not response.ok or not body.get("user"):
        raise ApiError.from_response(
            response.status_code, body, request_id=response.request_id
        )
    return User(**body["user"])
