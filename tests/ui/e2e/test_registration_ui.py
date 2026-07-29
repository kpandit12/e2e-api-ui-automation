"""E2E: register a new account through the real UI form."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import expect

from builders.user_builder import UserBuilder
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage


@allure.feature("Registration UI")
@pytest.mark.smoke
@pytest.mark.ui
def test_registering_a_new_account_redirects_to_login(
    registration_page: RegistrationPage, login_page: LoginPage
) -> None:
    new_user = UserBuilder().build()
    registration_page.open()
    registration_page.register(new_user.email, new_user.password)
    expect(login_page.page).to_have_url(f"{login_page.base_url}/#/login")


@allure.feature("Registration UI")
@pytest.mark.negative
@pytest.mark.ui
def test_registering_with_mismatched_passwords_shows_error(
    registration_page: RegistrationPage,
) -> None:
    new_user = UserBuilder().with_mismatched_repeat("something-else").build()
    registration_page.open()
    registration_page.email_input.fill(new_user.email)
    registration_page.password_input.fill(new_user.password)
    registration_page.repeat_password_input.fill(new_user.passwordRepeat)
    expect(registration_page.submit_button).to_be_disabled()
