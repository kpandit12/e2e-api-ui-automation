"""Base class shared by all Page Objects.

Owns the Playwright ``Page`` and the app's base URL, and centralises the one
Juice Shop quirk every page has to deal with: a cookie-consent banner and a
"Welcome Banner" dialog that pop up on first load and block interaction until
dismissed.
"""

from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Common navigation/dismissal helpers for every page object."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self, path: str = "/") -> None:
        """Navigate to ``path`` and dismiss the cookie/welcome overlays."""
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")
        self.dismiss_overlays()

    def dismiss_overlays(self) -> None:
        """Close the welcome dialog and cookie-consent banner if present.

        Both are best-effort: they only appear on a fresh session, so absence
        is not an error. Each locator is given a short window to appear so a
        slow-loading Angular overlay is still dismissed.
        """
        for selector in (
            "button.mat-dialog-close, [aria-label='Close Welcome Banner']",
            "#cookieconsent [aria-label='dismiss cookie message']",
        ):
            locator = self.page.locator(selector)
            try:
                locator.first.wait_for(state="visible", timeout=2000)
                locator.first.click(timeout=2000)
            except Exception:
                pass
