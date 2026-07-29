"""Unit tests for the auth DAO against a mocked transport."""
import pytest
import responses

from clients.rest_client import RestClient
from core.exceptions import ApiError, AuthenticationError
from core.retry_strategy import NoRetryStrategy
from dao import auth_dao

BASE_URL = "https://api.test.local"


def _client() -> RestClient:
    return RestClient(BASE_URL, retry_strategy=NoRetryStrategy())


@pytest.mark.unit
@responses.activate
def test_login_returns_token_on_success() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/rest/user/login",
        json={"authentication": {"token": "jwt-abc", "bid": 7, "umail": "a@b.com"}},
        status=200,
    )
    token = auth_dao.login(_client(), "a@b.com", "pw")
    assert token == "jwt-abc"


@pytest.mark.unit
@responses.activate
def test_authenticate_returns_token_and_basket_id() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/rest/user/login",
        json={"authentication": {"token": "jwt-abc", "bid": 7, "umail": "a@b.com"}},
        status=200,
    )
    auth = auth_dao.authenticate(_client(), "a@b.com", "pw")
    assert auth.token == "jwt-abc"
    assert auth.bid == 7


@pytest.mark.unit
@responses.activate
def test_login_raises_authentication_error_on_401() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/rest/user/login",
        json={"error": "Invalid email or password."},
        status=401,
    )
    with pytest.raises(AuthenticationError) as exc:
        auth_dao.login(_client(), "a@b.com", "wrong")
    assert exc.value.is_unauthorized()


@pytest.mark.unit
@responses.activate
def test_login_raises_api_error_on_unexpected_status() -> None:
    responses.add(
        responses.POST, f"{BASE_URL}/rest/user/login", json={}, status=500
    )
    with pytest.raises(ApiError) as exc:
        auth_dao.login(_client(), "a@b.com", "pw")
    assert exc.value.is_server_error()
