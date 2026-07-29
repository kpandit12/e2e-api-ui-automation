"""Integration tests for account registration (``POST /api/Users/``)."""
from __future__ import annotations

import allure
import pytest

from builders.user_builder import UserBuilder
from clients.rest_client import RestClient
from core.exceptions import ApiError
from dao import auth_dao, user_dao
from models.user import NewUser
from tests.support import attach_api_response


@allure.feature("Registration")
@pytest.mark.smoke
@pytest.mark.integration
def test_register_with_unique_email_succeeds(
    client: RestClient, new_user: NewUser
) -> None:
    response = user_dao.register_response(
        client, new_user.email, new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    attach_api_response("register response", response)
    assert response.status_code == 201


@allure.feature("Registration")
@pytest.mark.regression
@pytest.mark.integration
def test_registered_account_can_log_in(client: RestClient, new_user: NewUser) -> None:
    user_dao.register(
        client, new_user.email, new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    token = auth_dao.login(client, new_user.email, new_user.password)
    assert token


@allure.feature("Registration")
@pytest.mark.negative
@pytest.mark.integration
def test_duplicate_email_is_rejected(client: RestClient, new_user: NewUser) -> None:
    user_dao.register(
        client, new_user.email, new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    with pytest.raises(ApiError) as exc:
        user_dao.register(
            client, new_user.email, new_user.password,
            password_repeat=new_user.passwordRepeat,
        )
    assert exc.value.is_bad_request() or exc.value.is_conflict()


@allure.feature("Registration")
@pytest.mark.negative
@pytest.mark.integration
def test_mismatched_password_repeat_is_not_validated_server_side(
    client: RestClient,
) -> None:
    """Documents an observed API gap: Juice Shop's ``POST /api/Users/`` never
    checks that ``password`` and ``passwordRepeat`` match -- that rule is
    enforced only client-side, in the Angular registration form (covered by
    tests/ui/e2e/test_registration_ui.py::test_registering_with_mismatched_passwords_shows_error).
    A client that bypasses the UI (as this test does) can register an account
    with a passwordRepeat that never matches the real password.
    """
    bad_user = UserBuilder().with_mismatched_repeat("something-else").build()
    user_id = user_dao.register(
        client, bad_user.email, bad_user.password,
        password_repeat=bad_user.passwordRepeat,
    )
    assert user_id > 0
