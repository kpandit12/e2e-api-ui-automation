"""Page Object for the Juice Shop login screen (``/#/login``)."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Log in with email/password and read back any validation error."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.submit_button = page.locator("#loginButton")
        self.error_message = page.locator(".error, [aria-label='error']")

    def open(self) -> LoginPage:
        """Navigate to the login screen."""
        self.goto("/#/login")
        return self

    def login(self, email: str, password: str) -> None:
        """Fill the form and submit."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()

    def error_text(self) -> str:
        """Return the visible validation/auth error text, if any."""
        return self.error_message.first.inner_text()
