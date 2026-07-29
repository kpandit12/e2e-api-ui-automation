"""Structured logging setup.

Emits single-line ``key=value`` records so CI output is greppable and each log
line can be correlated to a specific request via a ``request_id``. A
``ContextVar`` carries the current correlation id without threading it through
every function signature, which also keeps it correct under pytest-xdist
workers and threads.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any

_request_id: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    """Bind a correlation id to the current execution context."""
    _request_id.set(request_id)


def get_request_id() -> str:
    """Return the correlation id bound to the current context (or ``-``)."""
    return _request_id.get()


class _RequestIdFilter(logging.Filter):
    """Injects the current correlation id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class _KeyValueFormatter(logging.Formatter):
    """Formats records as ``ts level logger request_id msg key=value ...``."""

    def format(self, record: logging.LogRecord) -> str:
        base = (
            f"ts={self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} "
            f"level={record.levelname} "
            f"logger={record.name} "
            f"request_id={getattr(record, 'request_id', '-')} "
            f"msg={record.getMessage()!r}"
        )
        extra = getattr(record, "context", None)
        if isinstance(extra, dict):
            kv = " ".join(f"{k}={v!r}" for k, v in extra.items())
            base = f"{base} {kv}"
        return base


def configure_logging(level: int = logging.INFO) -> None:
    """Idempotently configure the root ``restful_booker`` logger.

    Args:
        level: Minimum level to emit. Defaults to ``INFO``.
    """
    logger = logging.getLogger("restful_booker")
    logger.setLevel(level)
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(_KeyValueFormatter())
    handler.addFilter(_RequestIdFilter())
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str) -> logging.LoggerAdapter[Any]:
    """Return a namespaced logger under the ``restful_booker`` tree."""
    return logging.LoggerAdapter(logging.getLogger(f"restful_booker.{name}"), {})
