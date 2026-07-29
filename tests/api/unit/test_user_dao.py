"""Unit tests for the user DAO against a mocked transport."""
from typing import Any

import pytest
import responses

from clients.rest_client import RestClient
from core.exceptions import ApiError
from core.retry_strategy import NoRetryStrategy
from dao import user_dao

BASE_URL = "https://api.test.local"


def _client(**kwargs: Any) -> RestClient:
    kwargs.setdefault("retry_strategy", NoRetryStrategy())
    return RestClient(BASE_URL, **kwargs)


@pytest.mark.unit
@responses.activate
def test_register_returns_new_user_id() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/Users/",
        json={"data": {"id": 42, "email": "a@b.com"}},
        status=201,
    )
    assert user_dao.register(_client(), "a@b.com", "pw12345") == 42


@pytest.mark.unit
@responses.activate
def test_register_raises_conflict_on_duplicate_email() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/Users/",
        json={"errors": ["email already exists"]},
        status=400,
    )
    with pytest.raises(ApiError) as exc:
        user_dao.register(_client(), "dup@b.com", "pw12345")
    assert exc.value.is_bad_request()


@pytest.mark.unit
@responses.activate
def test_whoami_returns_authenticated_user() -> None:
    responses.add(
        responses.GET,
        f"{BASE_URL}/rest/user/whoami",
        json={"user": {"id": 1, "email": "a@b.com", "role": "customer"}},
        status=200,
    )
    user = user_dao.whoami(_client(token="jwt"))
    assert user.email == "a@b.com"


@pytest.mark.unit
@responses.activate
def test_whoami_raises_when_no_user_logged_in() -> None:
    responses.add(
        responses.GET, f"{BASE_URL}/rest/user/whoami", json={"user": None}, status=200
    )
    with pytest.raises(ApiError):
        user_dao.whoami(_client(token="jwt"))
