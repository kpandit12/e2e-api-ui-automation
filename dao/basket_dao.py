"""DAO for basket endpoints (``/rest/basket``, ``/api/BasketItems``)."""
from __future__ import annotations

from typing import Any

from clients.rest_client import ApiResponse, RestClient
from core.exceptions import ApiError


def get_basket_response(client: RestClient, basket_id: int | str) -> ApiResponse:
    """``GET /rest/basket/:id`` returning the raw response."""
    return client.get(f"/rest/basket/{basket_id}", authenticated=True)


def get_basket(client: RestClient, basket_id: int | str) -> dict[str, Any]:
    """``GET /rest/basket/:id`` -> the basket's ``data`` payload.

    Raises:
        ApiError: If the basket cannot be fetched (e.g. wrong owner).
    """
    response = get_basket_response(client, basket_id)
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
    return dict((response.json or {}).get("data", {}))


def add_item_response(
    client: RestClient, basket_id: int | str, product_id: int, quantity: int = 1
) -> ApiResponse:
    """``POST /api/BasketItems/`` returning the raw response."""
    return client.post(
        "/api/BasketItems/",
        json={"BasketId": basket_id, "ProductId": product_id, "quantity": quantity},
        authenticated=True,
    )


def add_item(
    client: RestClient, basket_id: int | str, product_id: int, quantity: int = 1
) -> int:
    """``POST /api/BasketItems/`` -> the new basket item's id.

    Raises:
        ApiError: If the item cannot be added (e.g. invalid product id).
    """
    response = add_item_response(client, basket_id, product_id, quantity)
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
    return int(response.json["data"]["id"])


def delete_item_response(client: RestClient, item_id: int) -> ApiResponse:
    """``DELETE /api/BasketItems/:id`` returning the raw response."""
    return client.delete(f"/api/BasketItems/{item_id}", authenticated=True)


def delete_item(client: RestClient, item_id: int) -> None:
    """``DELETE /api/BasketItems/:id``.

    Raises:
        ApiError: If the item cannot be deleted (e.g. already gone).
    """
    response = delete_item_response(client, item_id)
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
