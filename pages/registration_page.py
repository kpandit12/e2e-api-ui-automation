"""Page Object for the Juice Shop registration screen (``/#/register``)."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class RegistrationPage(BasePage):
    """Register a new account, including the mandatory security question."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.email_input = page.locator("#emailControl")
        self.password_input = page.locator("#passwordControl")
        self.repeat_password_input = page.locator("#repeatPasswordControl")
        self.security_question_select = page.locator(
            "mat-select[name='securityQuestion']"
        )
        self.security_answer_input = page.locator("#securityAnswerControl")
        self.submit_button = page.locator("#registerButton")

    def open(self) -> RegistrationPage:
        """Navigate to the registration screen."""
        self.goto("/#/register")
        return self

    def register(
        self, email: str, password: str, *, security_answer: str = "automation"
    ) -> None:
        """Fill and submit the registration form, picking the first
        available security question so callers don't have to know its exact
        wording.
        """
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.repeat_password_input.fill(password)
        # force=True: Angular Material's floating label visually overlaps the
        # select trigger, failing Playwright's actionability check even
        # though the element is genuinely clickable.
        self.security_question_select.click(force=True)
        self.page.locator("mat-option").first.click()
        self.security_answer_input.fill(security_answer)
        self.submit_button.click()
