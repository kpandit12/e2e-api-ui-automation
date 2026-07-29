"""Unit tests for the basket DAO against a mocked transport."""
from typing import Any

import pytest
import responses

from clients.rest_client import RestClient
from core.exceptions import ApiError
from core.retry_strategy import NoRetryStrategy
from dao import basket_dao

BASE_URL = "https://api.test.local"


def _client(**kwargs: Any) -> RestClient:
    kwargs.setdefault("retry_strategy", NoRetryStrategy())
    return RestClient(BASE_URL, **kwargs)


@pytest.mark.unit
@responses.activate
def test_get_basket_returns_data_payload() -> None:
    responses.add(
        responses.GET,
        f"{BASE_URL}/rest/basket/7",
        json={"data": {"id": 7, "Products": []}},
        status=200,
    )
    basket = basket_dao.get_basket(_client(token="jwt"), 7)
    assert basket["id"] == 7


@pytest.mark.unit
@responses.activate
def test_add_item_returns_new_item_id() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/BasketItems/",
        json={"data": {"id": 100, "BasketId": 7, "ProductId": 1, "quantity": 1}},
        status=201,
    )
    item_id = basket_dao.add_item(_client(token="jwt"), 7, 1)
    assert item_id == 100


@pytest.mark.unit
@responses.activate
def test_add_item_raises_on_invalid_product() -> None:
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/BasketItems/",
        json={"errors": ["Product not found"]},
        status=500,
    )
    with pytest.raises(ApiError) as exc:
        basket_dao.add_item(_client(token="jwt"), 7, 9999)
    assert exc.value.is_server_error()


@pytest.mark.unit
@responses.activate
def test_delete_item_succeeds_silently() -> None:
    responses.add(
        responses.DELETE, f"{BASE_URL}/api/BasketItems/100", json={}, status=200
    )
    basket_dao.delete_item(_client(token="jwt"), 100)  # no exception raised
