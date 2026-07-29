"""Request/response logger collaborator.

Used by ``RestClient`` so logging is swappable and independently testable.
Sensitive material (auth tokens, cookies) is masked before anything is emitted
or attached to a report.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from requests import Response

from core.logging_config import get_logger

_TOKEN_MASK = "***MASKED***"
_SENSITIVE_KEYS = {"authorization", "cookie"}


def mask_value(value: str) -> str:
    """Redact a header/cookie value that may carry a token."""
    if not value:
        return value
    parts = value.split()
    if len(parts) == 2 and parts[0].lower() in {"bearer", "token"}:
        return f"{parts[0]} {_TOKEN_MASK}"
    return _TOKEN_MASK


def mask_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of ``headers`` with sensitive values redacted."""
    masked = dict(headers)
    for key in list(masked):
        low = key.lower()
        if low in _SENSITIVE_KEYS or "token" in low:
            masked[key] = mask_value(masked[key])
    return masked


class RequestLogger:
    """Structured logger for outbound requests and inbound responses."""

    def __init__(self) -> None:
        self._log = get_logger("http")

    def log_request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any | None = None,
    ) -> None:
        """Emit a structured line describing an outbound request."""
        self._log.info(
            "http_request",
            extra={
                "context": {
                    "method": method.upper(),
                    "url": url,
                    "params": dict(params) if params else None,
                    "headers": mask_headers(headers) if headers else None,
                    "body": body,
                }
            },
        )

    def log_response(self, method: str, url: str, response: Response) -> None:
        """Emit a structured line describing an inbound response."""
        self._log.info(
            "http_response",
            extra={
                "context": {
                    "method": method.upper(),
                    "url": url,
                    "status": response.status_code,
                    "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
                    "body_preview": response.text[:500],
                }
            },
        )
