"""Integration tests for the basket flow (search -> add -> view -> delete)."""
from __future__ import annotations

import allure
import pytest

from clients.rest_client import RestClient
from core.exceptions import ApiError
from dao import basket_dao, product_dao
from tests.api.integration.conftest import RegisteredUser
from utils.ecommerce_workflows import add_first_search_result_to_basket


@allure.feature("Basket")
@pytest.mark.smoke
@pytest.mark.integration
def test_add_product_to_basket_and_view_it(
    client: RestClient, registered_user: RegisteredUser
) -> None:
    basket_id = registered_user.basket_id
    assert basket_id is not None
    item_id = add_first_search_result_to_basket(
        client, registered_user.token, basket_id, "apple"
    )
    assert item_id > 0
    basket = basket_dao.get_basket(client, basket_id)
    assert basket.get("id") == basket_id


@allure.feature("Basket")
@pytest.mark.regression
@pytest.mark.integration
def test_delete_basket_item_removes_it(
    client: RestClient, registered_user: RegisteredUser
) -> None:
    basket_id = registered_user.basket_id
    assert basket_id is not None
    products = product_dao.search_products(client, "apple")
    item_id = basket_dao.add_item(client, basket_id, products[0].id)
    basket_dao.delete_item(client, item_id)
    with pytest.raises(ApiError):
        basket_dao.delete_item(client, item_id)  # already gone


@allure.feature("Basket")
@pytest.mark.negative
@pytest.mark.integration
def test_add_item_with_invalid_product_id_is_rejected(
    client: RestClient, registered_user: RegisteredUser
) -> None:
    basket_id = registered_user.basket_id
    assert basket_id is not None
    with pytest.raises(ApiError) as exc:
        basket_dao.add_item(client, basket_id, 999999)
    assert exc.value.status is not None and exc.value.status >= 400


@allure.feature("Basket")
@pytest.mark.negative
@pytest.mark.integration
def test_get_basket_without_token_is_rejected(client: RestClient) -> None:
    # basket_dao.get_basket forces authenticated=True and would raise a
    # client-side TransportError before ever reaching the server (see
    # tests/api/unit/test_rest_client.py::test_authenticated_without_token_raises).
    # This test exercises the server's own rejection of a request that
    # carries no Authorization header at all, so it calls the client raw.
    response = client.get("/rest/basket/1")
    assert response.status_code in (401, 403)
