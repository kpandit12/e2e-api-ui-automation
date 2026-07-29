"""Page Object for the shopping basket screen (``/#/basket``)."""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class BasketPage(BasePage):
    """Open the basket from the toolbar and read back its contents."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.cart_button = page.locator(
            "button[aria-label='Show the shopping cart'], #cartButton"
        )
        self.item_rows = page.locator("mat-row, tr.mat-row")
        self.checkout_button = page.get_by_role("button", name="Checkout")

    def open_via_toolbar(self) -> BasketPage:
        """Click the toolbar cart icon to navigate to the basket."""
        self.cart_button.click()
        return self

    def open(self) -> BasketPage:
        """Navigate directly to the basket screen."""
        self.goto("/#/basket")
        return self

    def item_count(self) -> int:
        """Number of line items currently in the basket."""
        return self.item_rows.count()
