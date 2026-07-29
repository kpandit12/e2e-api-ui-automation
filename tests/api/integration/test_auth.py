"""Integration tests for login/whoami (``POST /rest/user/login``, whoami)."""
from __future__ import annotations

import allure
import pytest

from clients.rest_client import RestClient
from core.exceptions import ApiError
from dao import auth_dao, user_dao
from tests.api.integration.conftest import RegisteredUser
from tests.support import attach_api_response


@allure.feature("Auth")
@pytest.mark.smoke
@pytest.mark.integration
def test_registered_user_whoami_returns_own_email(
    client: RestClient, registered_user: RegisteredUser
) -> None:
    user = user_dao.whoami(client)
    assert user.email == registered_user.new_user.email


@allure.feature("Auth")
@pytest.mark.negative
@pytest.mark.integration
def test_login_with_wrong_password_is_rejected(
    client: RestClient, registered_user: RegisteredUser
) -> None:
    with pytest.raises(ApiError) as exc:
        auth_dao.login(client, registered_user.new_user.email, "definitely-wrong")
    assert exc.value.is_unauthorized()


@allure.feature("Auth")
@pytest.mark.negative
@pytest.mark.integration
def test_whoami_without_token_is_rejected(client: RestClient) -> None:
    response = user_dao.whoami_response(client)
    attach_api_response("whoami without token", response)
    assert response.status_code in (401, 403) or not (response.json or {}).get(
        "user"
    )
