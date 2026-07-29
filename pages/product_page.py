"""Page Object for the product listing/search screen (``/#/search``)."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductPage(BasePage):
    """Search the catalogue and add items to the basket from the grid."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.search_toggle = page.get_by_role("button", name="Open search")
        self.search_input = page.locator("#searchQuery input")
        self.product_cards = page.locator("app-search-result mat-card")

    def open(self) -> ProductPage:
        """Navigate to the product listing screen."""
        self.goto("/#/search")
        return self

    def search(self, query: str) -> ProductPage:
        """Type ``query`` into the search box and submit.

        The search box (``app-mat-search-bar``) starts collapsed to just an
        icon button; it must be opened before its ``<input>`` is interactable.
        """
        if self.search_toggle.is_visible():
            # force=True: the search-bar's decorative container overlaps the
            # toggle button and fails Playwright's actionability check even
            # though the button is genuinely clickable.
            self.search_toggle.click(force=True)
        self.search_input.click(force=True)
        self.search_input.fill(query)
        self.search_input.press("Enter")
        return self

    def result_count(self) -> int:
        """Number of product cards currently displayed.

        Filters out any placeholder/no-results cards by requiring an
        "Add to Basket" button.
        """
        return self.product_cards.filter(
            has=self.page.get_by_role("button", name="Add to Basket")
        ).count()

    def add_to_basket_by_name(self, product_name: str) -> None:
        """Click "Add to Basket" on the card matching ``product_name``."""
        card = self.page.locator(
            "app-search-result mat-card",
            has=self.page.get_by_text(product_name, exact=False),
        )
        card.first.get_by_role("button", name="Add to Basket").click()
