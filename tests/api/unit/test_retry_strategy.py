"""Unit tests for the retry Strategy implementations (no network)."""

from unittest.mock import Mock

import pytest

from core.retry_strategy import ExponentialBackoffStrategy, NoRetryStrategy


def _response(status: int) -> Mock:
    resp = Mock()
    resp.status_code = status
    return resp


@pytest.mark.unit
def test_no_retry_sends_once() -> None:
    send = Mock(return_value=_response(503))
    result = NoRetryStrategy().execute(send)
    assert send.call_count == 1
    assert result.status_code == 503


@pytest.mark.unit
def test_backoff_retries_gateway_errors_until_success() -> None:
    sleeps: list[float] = []
    send = Mock(side_effect=[_response(503), _response(502), _response(200)])
    strategy = ExponentialBackoffStrategy(
        max_attempts=3, backoff_factor=0.1, sleep=sleeps.append
    )
    result = strategy.execute(send)
    assert result.status_code == 200
    assert send.call_count == 3
    assert sleeps == [0.1, 0.2]  # exponential growth


@pytest.mark.unit
def test_backoff_stops_after_max_attempts() -> None:
    send = Mock(return_value=_response(503))
    strategy = ExponentialBackoffStrategy(
        max_attempts=3, backoff_factor=0.0, sleep=lambda _: None
    )
    result = strategy.execute(send)
    assert result.status_code == 503
    assert send.call_count == 3


@pytest.mark.unit
def test_non_retryable_status_is_not_retried() -> None:
    send = Mock(return_value=_response(404))
    strategy = ExponentialBackoffStrategy(max_attempts=5, sleep=lambda _: None)
    strategy.execute(send)
    assert send.call_count == 1


@pytest.mark.unit
def test_rate_limit_is_not_retried_by_default() -> None:
    """429 is intentionally not in the RestClient's default retry set."""
    send = Mock(return_value=_response(429))
    strategy = ExponentialBackoffStrategy(max_attempts=5, sleep=lambda _: None)
    strategy.execute(send)
    assert send.call_count == 1


@pytest.mark.unit
def test_504_is_retried() -> None:
    send = Mock(side_effect=[_response(504), _response(200)])
    strategy = ExponentialBackoffStrategy(max_attempts=3, sleep=lambda _: None)
    result = strategy.execute(send)
    assert result.status_code == 200
    assert send.call_count == 2


@pytest.mark.unit
def test_invalid_max_attempts_rejected() -> None:
    with pytest.raises(ValueError):
        ExponentialBackoffStrategy(max_attempts=0)
