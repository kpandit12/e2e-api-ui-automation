"""Retry behaviour modelled with the Strategy pattern.

The client depends on the ``RetryStrategy`` abstraction, not a concrete retry
implementation. This lets a caller inject exponential backoff in production, a
no-op strategy in unit tests (so mocked requests run instantly), or a custom
policy per client -- all without editing ``RestClient``.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable

from requests import Response

from core.logging_config import get_logger

logger = get_logger("retry")

# Transient gateway/service statuses that are safe to retry. Restricted to the
# 502/503/504 family (matching the production RestClient policy): these signal a
# transient upstream/proxy failure, not a client mistake.
DEFAULT_RETRYABLE_STATUS = frozenset({502, 503, 504})


class RetryStrategy(ABC):
    """Strategy interface: decide whether/when to re-issue a request."""

    @abstractmethod
    def execute(self, send: Callable[[], Response]) -> Response:
        """Invoke ``send`` and apply the strategy's retry policy.

        Args:
            send: A zero-arg callable that performs one HTTP attempt.

        Returns:
            The final :class:`requests.Response`.
        """
        raise NotImplementedError


class NoRetryStrategy(RetryStrategy):
    """Sends exactly once. Ideal for unit tests and non-idempotent calls."""

    def execute(self, send: Callable[[], Response]) -> Response:
        return send()


class ExponentialBackoffStrategy(RetryStrategy):
    """Retries transient statuses with exponential backoff.

    Args:
        max_attempts: Total number of attempts (>= 1).
        backoff_factor: Base delay in seconds; attempt *n* waits
            ``backoff_factor * 2**(n-1)``.
        retryable_status: Status codes that trigger a retry.
        sleep: Injectable sleep function (defaults to :func:`time.sleep`),
            overridden in tests to keep them fast.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_factor: float = 0.5,
        retryable_status: frozenset[int] = DEFAULT_RETRYABLE_STATUS,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self._max_attempts = max_attempts
        self._backoff_factor = backoff_factor
        self._retryable_status = retryable_status
        self._sleep = sleep

    def execute(self, send: Callable[[], Response]) -> Response:
        response = send()
        for attempt in range(1, self._max_attempts):
            if response.status_code not in self._retryable_status:
                return response
            delay = self._backoff_factor * (2 ** (attempt - 1))
            logger.warning(
                "retrying request",
                extra={
                    "context": {
                        "attempt": attempt,
                        "status": response.status_code,
                        "delay_s": delay,
                    }
                },
            )
            self._sleep(delay)
            response = send()
        return response
