"""Layer 1 — the RestClient.

``RestClient`` is the single object that touches ``requests``. It owns the
``requests.Session``, sets the JSON content-type, attaches the auth token,
logs every request/response (masking secrets), and retries transient
gateway failures (502/503/504) with exponential backoff. Nothing outside this
module talks to ``requests`` directly; the DAO layer calls ``RestClient``.

Retry policy, request logging and (optionally) the auth token are supplied by
*composition* so each concern stays independently swappable and testable.
"""
from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import requests
from requests import Response, Session
from requests.exceptions import RequestException

from core.exceptions import TransportError
from core.logging_config import get_logger, set_request_id
from core.request_logger import RequestLogger
from core.retry_strategy import ExponentialBackoffStrategy, RetryStrategy

logger = get_logger("client")


@dataclass(frozen=True)
class ApiResponse:
    """Immutable value object returned by the client.

    Decouples the DAO layer from the raw ``requests.Response`` so callers depend
    only on the fields they need, and every response carries the ``request_id``
    used to correlate it with the structured logs.
    """

    status_code: int
    json: Any
    text: str
    headers: Mapping[str, str]
    request_id: str

    @property
    def ok(self) -> bool:
        """True for 2xx responses."""
        return 200 <= self.status_code < 300


class RestClient:
    """Encapsulated, composable HTTP client — the only caller of ``requests``.

    Args:
        base_url: Root URL of the target API.
        timeout: Per-request timeout in seconds.
        retry_strategy: Injected retry policy (Strategy pattern). Defaults to
            :class:`ExponentialBackoffStrategy` (retries 502/503/504).
        request_logger: Injected structured request/response logger.
        token: Optional auth token; also settable later via :meth:`set_token`.
        session: Optional pre-built session (mainly for tests/mocking).
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        retry_strategy: RetryStrategy | None = None,
        request_logger: RequestLogger | None = None,
        token: str | None = None,
        session: Session | None = None,
    ) -> None:
        self.__base_url = base_url.rstrip("/")
        self.__timeout = timeout
        self.__retry = retry_strategy or ExponentialBackoffStrategy()
        self.__logger = request_logger or RequestLogger()
        self.__token = token
        self.__session = session or requests.Session()
        self.__session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        if token is not None:
            self.__session.cookies.set("token", token)

    # -- token management --------------------------------------------------- #
    def set_token(self, token: str) -> None:
        """Store the auth token attached to authenticated requests.

        Also mirrors the token into a ``token`` cookie: Juice Shop's
        ``/rest/user/whoami`` endpoint reads the JWT from that cookie rather
        than the ``Authorization`` header used by every other endpoint.
        """
        self.__token = token
        self.__session.cookies.set("token", token)

    @property
    def has_token(self) -> bool:
        """True once a token has been set."""
        return self.__token is not None

    # -- internal helpers --------------------------------------------------- #
    def _url(self, path: str) -> str:
        return f"{self.__base_url}/{path.lstrip('/')}"

    def _auth_header(self) -> dict[str, str]:
        if self.__token is None:
            raise TransportError(
                "authenticated request attempted but no token is set"
            )
        return {"Authorization": f"Bearer {self.__token}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
        authenticated: bool = False,
    ) -> ApiResponse:
        """Issue a request through the retry strategy and structured logger.

        Args:
            method: HTTP verb.
            path: Path relative to the base URL.
            params: Optional query parameters.
            json: Optional JSON body.
            headers: Optional extra headers (merged over auth headers).
            authenticated: When True, attach the stored auth token.

        Returns:
            An :class:`ApiResponse`.

        Raises:
            TransportError: If no HTTP response was produced (network failure).
        """
        request_id = uuid.uuid4().hex[:12]
        set_request_id(request_id)
        url = self._url(path)

        merged_headers: dict[str, str] = {}
        if authenticated:
            merged_headers.update(self._auth_header())
        if headers:
            merged_headers.update(headers)

        def _send() -> Response:
            self.__logger.log_request(
                method, url, params=params, headers=merged_headers, body=json
            )
            response = self.__session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=merged_headers or None,
                timeout=self.__timeout,
            )
            self.__logger.log_response(method, url, response)
            return response

        try:
            raw = self.__retry.execute(_send)
        except RequestException as exc:
            raise TransportError(
                f"transport failure for {method} {url}: {exc}",
                request_id=request_id,
            ) from exc

        return self._to_api_response(raw, request_id)

    @staticmethod
    def _to_api_response(raw: Response, request_id: str) -> ApiResponse:
        try:
            parsed: Any = raw.json()
        except ValueError:
            parsed = None
        return ApiResponse(
            status_code=raw.status_code,
            json=parsed,
            text=raw.text,
            headers=dict(raw.headers),
            request_id=request_id,
        )

    # -- verb helpers used by the DAO layer --------------------------------- #
    def get(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        """Release the underlying HTTP session."""
        self.__session.close()


def build_rest_client(settings: Any = None) -> RestClient:
    """Factory: build a RestClient wired for the active environment profile.

    Construction logic (base URL, timeout, retry policy per profile) lives here
    so call sites just ask for a ready client. Authentication is deliberately
    left to the caller (the DAO ``create_token`` + :meth:`RestClient.set_token`)
    to keep this factory free of a circular dependency on the auth DAO.
    """
    from config.settings import get_settings
    from core.retry_strategy import NoRetryStrategy

    settings = settings or get_settings()
    if settings.profile == "unit":
        retry: RetryStrategy = NoRetryStrategy()
    elif settings.profile == "ci":
        retry = ExponentialBackoffStrategy(
            max_attempts=settings.max_retries + 2,
            backoff_factor=settings.backoff_factor,
        )
    else:
        retry = ExponentialBackoffStrategy(
            max_attempts=settings.max_retries,
            backoff_factor=settings.backoff_factor,
        )
    return RestClient(
        settings.api_base_url,
        timeout=settings.timeout,
        retry_strategy=retry,
        request_logger=RequestLogger(),
    )
