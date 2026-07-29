"""DAO for ``GET /rest/products/search``."""
from __future__ import annotations

from clients.rest_client import ApiResponse, RestClient
from core.exceptions import ApiError
from models.product import Product


def search_products_response(client: RestClient, query: str) -> ApiResponse:
    """``GET /rest/products/search?q=...`` returning the raw response."""
    return client.get("/rest/products/search", params={"q": query})


def search_products(client: RestClient, query: str) -> list[Product]:
    """``GET /rest/products/search?q=...`` -> matching products.

    Raises:
        ApiError: If the search endpoint itself fails.
    """
    response = search_products_response(client, query)
    if not response.ok:
        raise ApiError.from_response(
            response.status_code,
            response.json or response.text,
            request_id=response.request_id,
        )
    return [Product(**item) for item in (response.json or {}).get("data", [])]
