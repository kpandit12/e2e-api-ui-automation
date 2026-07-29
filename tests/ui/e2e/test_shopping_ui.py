"""E2E: search the catalogue and add an item to the basket through the UI."""
from __future__ import annotations

import uuid

import allure
import pytest
from playwright.sync_api import expect

from pages.basket_page import BasketPage
from pages.product_page import ProductPage


@allure.feature("Shopping UI")
@pytest.mark.smoke
@pytest.mark.ui
def test_searching_for_a_known_product_shows_results(product_page: ProductPage) -> None:
    product_page.open()
    product_page.search("apple")
    expect(product_page.product_cards.first).to_be_visible()


@allure.feature("Shopping UI")
@pytest.mark.regression
@pytest.mark.ui
def test_adding_a_product_to_basket_increments_cart(
    product_page: ProductPage, basket_page: BasketPage
) -> None:
    product_page.open()
    product_page.search("apple")
    product_page.add_to_basket_by_name("Apple")
    basket_page.open()
    expect(basket_page.item_rows.first).to_be_visible()


@allure.feature("Shopping UI")
@pytest.mark.regression
@pytest.mark.ui
def test_searching_for_nonsense_shows_no_results(product_page: ProductPage) -> None:
    product_page.open()
    # A random UUID string is extremely unlikely to match any product data.
    product_page.search(str(uuid.uuid4()))
    expect(
        product_page.product_cards.filter(
            has=product_page.page.get_by_role("button", name="Add to Basket")
        )
    ).to_have_count(0)
