"""Unit tests for the product DAO against a mocked transport."""
import pytest
import responses

from clients.rest_client import RestClient
from core.exceptions import ApiError
from core.retry_strategy import NoRetryStrategy
from dao import product_dao

BASE_URL = "https://api.test.local"


def _client() -> RestClient:
    return RestClient(BASE_URL, retry_strategy=NoRetryStrategy())


@pytest.mark.unit
@responses.activate
def test_search_products_returns_parsed_list() -> None:
    responses.add(
        responses.GET,
        f"{BASE_URL}/rest/products/search",
        json={
            "data": [
                {"id": 1, "name": "Apple Juice", "price": 1.99},
                {"id": 2, "name": "Apple Pressling", "price": 2.99},
            ]
        },
        status=200,
    )
    products = product_dao.search_products(_client(), "apple")
    assert [p.name for p in products] == ["Apple Juice", "Apple Pressling"]


@pytest.mark.unit
@responses.activate
def test_search_products_returns_empty_list_for_no_matches() -> None:
    responses.add(
        responses.GET,
        f"{BASE_URL}/rest/products/search",
        json={"data": []},
        status=200,
    )
    assert product_dao.search_products(_client(), "nonexistent") == []


@pytest.mark.unit
@responses.activate
def test_search_products_raises_on_server_error() -> None:
    responses.add(
        responses.GET, f"{BASE_URL}/rest/products/search", json={}, status=500
    )
    with pytest.raises(ApiError) as exc:
        product_dao.search_products(_client(), "apple")
    assert exc.value.is_server_error()
