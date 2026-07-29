"""Framework exception hierarchy.

The DAO layer translates transport-level outcomes (status codes, connection
errors) into a single ``ApiError`` carrying the failing ``status`` and response
``body``. Callers assert on *meaning* via convenience predicates
(``err.is_not_found()``) instead of inspecting raw status codes everywhere,
which keeps tests readable and decoupled from the wire format.

Thin subclasses (``ResourceNotFoundError`` etc.) are retained so callers may
also ``except`` a specific error type when that reads better; the DAO chooses
the most specific subclass automatically via :meth:`ApiError.from_response`.
"""

from __future__ import annotations

from typing import Any


class ApiError(Exception):
    """Raised by the DAO layer when an API call fails its status check.

    Args:
        status: The HTTP status code of the failing response.
        body: The parsed response body (or raw text) that came back.
        message: Optional human-readable description; a sensible default is
            derived from the status when omitted.
        request_id: Correlation id of the originating request, for log tracing.
    """

    def __init__(
        self,
        status: int | None,
        body: Any = None,
        *,
        message: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.status = status
        self.body = body
        self.request_id = request_id
        self.message = message or f"API call failed with status {status}"
        super().__init__(self.message)

    # -- convenience predicates (mirror the Dell IAM framework) ------------- #
    def is_unauthorized(self) -> bool:
        """True for 401/403 (missing or rejected credentials)."""
        return self.status in (401, 403)

    def is_not_found(self) -> bool:
        """True for 404 (resource does not exist)."""
        return self.status == 404

    def is_conflict(self) -> bool:
        """True for 409 (state conflict)."""
        return self.status == 409

    def is_bad_request(self) -> bool:
        """True for any non-auth/not-found 4xx (malformed/rejected request)."""
        return self.status is not None and 400 <= self.status < 500

    def is_server_error(self) -> bool:
        """True for any 5xx (server-side failure, after retries)."""
        return self.status is not None and 500 <= self.status < 600

    @classmethod
    def from_response(
        cls,
        status: int | None,
        body: Any = None,
        *,
        message: str | None = None,
        request_id: str | None = None,
    ) -> ApiError:
        """Build the most specific ``ApiError`` subclass for a status code."""
        subclass: type[ApiError]
        if status in (401, 403):
            subclass = AuthenticationError
        elif status == 404:
            subclass = ResourceNotFoundError
        elif status == 409:
            subclass = ConflictError
        elif status is not None and 400 <= status < 500:
            subclass = BadRequestError
        elif status is not None and status >= 500:
            subclass = ServerError
        else:
            subclass = cls
        return subclass(status, body, message=message, request_id=request_id)

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        parts = [self.message]
        if self.request_id is not None:
            parts.append(f"request_id={self.request_id}")
        return " ".join(parts)


class AuthenticationError(ApiError):
    """Raised when credentials are rejected or a protected call lacks a token."""

    def is_unauthorized(self) -> bool:
        return True


class ResourceNotFoundError(ApiError):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def is_not_found(self) -> bool:
        return True


class ConflictError(ApiError):
    """Raised when the request conflicts with current state (HTTP 409)."""

    def is_conflict(self) -> bool:
        return True


class BadRequestError(ApiError):
    """Raised when the API rejects a payload as malformed (HTTP 4xx)."""

    def is_bad_request(self) -> bool:
        return True


class ServerError(ApiError):
    """Raised when the API returns a 5xx after retries are exhausted."""

    def is_server_error(self) -> bool:
        return True


class TransportError(ApiError):
    """Raised when the request never produced an HTTP response (network error)."""

    def __init__(
        self,
        message: str,
        *,
        request_id: str | None = None,
    ) -> None:
        super().__init__(None, None, message=message, request_id=request_id)
