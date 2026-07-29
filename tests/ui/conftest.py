"""UI-layer fixtures.

Built on top of ``pytest-playwright``, which already provides a function-
scoped ``page`` fixture (fresh browser context per test — the UI analogue of
the API layer's "own resources per test" parallel-safety rule). This module
wires that ``page`` into our Page Objects and reads ``headless``/``browser``
from :mod:`config.settings` instead of hardcoding them.
"""
from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import Page

from config.settings import get_settings
from pages.basket_page import BasketPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.registration_page import RegistrationPage


@pytest.fixture(scope="session")
def browser_name() -> str:
    """Return the browser engine configured in Settings (QA_BROWSER)."""
    return get_settings().browser


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any],
) -> dict[str, Any]:
    """Respect ``QA_HEADLESS`` from Settings instead of pytest-playwright's default."""
    settings = get_settings()
    return {**browser_type_launch_args, "headless": settings.headless}


@pytest.fixture()
def ui_base_url() -> str:
    return get_settings().ui_base_url


@pytest.fixture()
def login_page(page: Page, ui_base_url: str) -> LoginPage:
    return LoginPage(page, ui_base_url)


@pytest.fixture()
def registration_page(page: Page, ui_base_url: str) -> RegistrationPage:
    return RegistrationPage(page, ui_base_url)


@pytest.fixture()
def product_page(page: Page, ui_base_url: str) -> ProductPage:
    return ProductPage(page, ui_base_url)


@pytest.fixture()
def basket_page(page: Page, ui_base_url: str) -> BasketPage:
    return BasketPage(page, ui_base_url)
