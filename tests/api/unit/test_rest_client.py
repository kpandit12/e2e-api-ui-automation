"""Unit tests for the RestClient against a mocked transport."""
from typing import Any

import pytest
import responses
from requests.exceptions import ConnectionError as RequestsConnectionError

from clients.rest_client import RestClient
from core.exceptions import (
    ApiError,
    AuthenticationError,
    BadRequestError,
    ResourceNotFoundError,
    ServerError,
    TransportError,
)
from core.retry_strategy import ExponentialBackoffStrategy, NoRetryStrategy

BASE_URL = "https://api.test.local"


def _client(**kwargs: Any) -> RestClient:
    kwargs.setdefault("retry_strategy", NoRetryStrategy())
    return RestClient(BASE_URL, **kwargs)


@pytest.mark.unit
@responses.activate
def test_get_parses_json_and_status() -> None:
    responses.add(responses.GET, f"{BASE_URL}/thing", json={"a": 1}, status=200)
    result = _client().get("/thing")
    assert result.status_code == 200
    assert result.json == {"a": 1}
    assert result.ok
    assert result.request_id  # correlation id populated


@pytest.mark.unit
@responses.activate
def test_retries_transient_then_succeeds() -> None:
    responses.add(responses.GET, f"{BASE_URL}/flaky", status=503)
    responses.add(responses.GET, f"{BASE_URL}/flaky", status=503)
    responses.add(responses.GET, f"{BASE_URL}/flaky", json={"ok": True}, status=200)
    client = _client(
        retry_strategy=ExponentialBackoffStrategy(
            max_attempts=3, backoff_factor=0.0, sleep=lambda _: None
        )
    )
    result = client.get("/flaky")
    assert result.status_code == 200
    assert len(responses.calls) == 3


@pytest.mark.unit
@responses.activate
def test_gateway_errors_are_retried_but_not_429() -> None:
    """RestClient retries 502/503/504, not 429 (per the production policy)."""
    responses.add(responses.GET, f"{BASE_URL}/x", status=429)
    result = _client(
        retry_strategy=ExponentialBackoffStrategy(
            max_attempts=3, backoff_factor=0.0, sleep=lambda _: None
        )
    ).get("/x")
    assert result.status_code == 429
    assert len(responses.calls) == 1  # not retried


@pytest.mark.unit
@responses.activate
def test_connection_error_becomes_transport_error() -> None:
    responses.add(
        responses.GET,
        f"{BASE_URL}/down",
        body=RequestsConnectionError("boom"),
    )
    with pytest.raises(TransportError):
        _client().get("/down")


@pytest.mark.unit
@responses.activate
def test_authenticated_request_attaches_bearer_token() -> None:
    responses.add(responses.DELETE, f"{BASE_URL}/api/BasketItems/1", status=200)
    client = _client(token="secret-abc")
    client.delete("/api/BasketItems/1", authenticated=True)
    sent = responses.calls[0].request
    assert sent.headers["Authorization"] == "Bearer secret-abc"


@pytest.mark.unit
def test_authenticated_without_token_raises() -> None:
    with pytest.raises(TransportError):
        _client().delete("/api/BasketItems/1", authenticated=True)


@pytest.mark.unit
@pytest.mark.parametrize(
    "status,exc",
    [
        (401, AuthenticationError),
        (403, AuthenticationError),
        (404, ResourceNotFoundError),
        (409, ApiError),
        (400, BadRequestError),
        (405, BadRequestError),
        (500, ServerError),
    ],
)
@responses.activate
def test_api_error_from_response_selects_correct_subclass(
    status: int, exc: type[ApiError]
) -> None:
    """The predicate-based exception factory maps statuses to subclasses."""
    err = ApiError.from_response(status, {})
    assert isinstance(err, exc)
    assert err.status == status
