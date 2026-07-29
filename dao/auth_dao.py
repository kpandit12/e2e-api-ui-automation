"""DAO for ``POST /rest/user/login``.

Juice Shop returns HTTP 200 with ``{"authentication": {"token": ...}}`` on
success and HTTP 401 with an error body on bad credentials, so :func:`login`
can branch on the status code.
"""

from __future__ import annotations

from clients.rest_client import ApiResponse, RestClient
from core.exceptions import ApiError
from models.auth import Authentication, LoginResponse


def login_response(client: RestClient, email: str, password: str) -> ApiResponse:
    """``POST /rest/user/login`` returning the raw response (for negative tests)."""
    return client.post("/rest/user/login", json={"email": email, "password": password})


def authenticate(client: RestClient, email: str, password: str) -> Authentication:
    """``POST /rest/user/login`` -> the validated ``authentication`` object
    (token + basket id), for callers that need more than just the token.

    Raises:
        ApiError: If the API rejects the credentials (typically 401).
    """
    response = login_response(client, email, password)
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
    return LoginResponse(**response.json).authentication


def login(client: RestClient, email: str, password: str) -> str:
    """``POST /rest/user/login`` -> validated JWT string.

    Raises:
        ApiError: If the API rejects the credentials (typically 401).
    """
    return authenticate(client, email, password).token
