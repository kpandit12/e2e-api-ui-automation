"""E2E: log in through the real UI, including the negative path."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import expect

from builders.user_builder import UserBuilder
from clients.rest_client import RestClient
from dao import auth_dao, user_dao
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage


@allure.feature("Login UI")
@pytest.mark.smoke
@pytest.mark.ui
def test_login_with_valid_credentials_reaches_account_menu(
    client: RestClient, login_page: LoginPage
) -> None:
    new_user = UserBuilder().build()
    user_dao.register(
        client,
        new_user.email,
        new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    login_page.open()
    login_page.login(new_user.email, new_user.password)
    expect(login_page.page.locator("#navbarAccount")).to_be_visible()


@allure.feature("Login UI")
@pytest.mark.negative
@pytest.mark.ui
def test_login_with_wrong_password_shows_error(
    client: RestClient, login_page: LoginPage
) -> None:
    new_user = UserBuilder().build()
    user_dao.register(
        client,
        new_user.email,
        new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    login_page.open()
    login_page.login(new_user.email, "definitely-wrong")
    expect(login_page.error_message.first).to_be_visible()


@allure.feature("Login UI")
@pytest.mark.regression
@pytest.mark.ui
def test_ui_registration_then_api_login_succeeds(
    client: RestClient, registration_page: RegistrationPage
) -> None:
    """Hybrid check: the account the UI created is genuinely usable via the API."""
    new_user = UserBuilder().build()
    registration_page.open()
    registration_page.register(new_user.email, new_user.password)
    token = auth_dao.login(client, new_user.email, new_user.password)
    assert token
