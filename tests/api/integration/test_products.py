"""Integration tests for product search (``GET /rest/products/search``)."""
from __future__ import annotations

import allure
import pytest

from clients.rest_client import RestClient
from dao import product_dao


@allure.feature("Products")
@pytest.mark.smoke
@pytest.mark.integration
def test_search_for_known_term_returns_results(client: RestClient) -> None:
    products = product_dao.search_products(client, "apple")
    assert len(products) > 0
    assert all(p.id is not None for p in products)


@allure.feature("Products")
@pytest.mark.regression
@pytest.mark.integration
def test_search_for_nonsense_term_returns_no_results(client: RestClient) -> None:
    products = product_dao.search_products(client, "zzzznonexistentquery9999")
    assert products == []


@allure.feature("Products")
@pytest.mark.regression
@pytest.mark.integration
def test_empty_query_returns_full_catalogue(client: RestClient) -> None:
    products = product_dao.search_products(client, "")
    assert len(products) > 0
