"""Layer 3 — orchestration helpers that compose several DAO calls.

These live above both the API and UI tests so multi-step business flows
(register, log in, search, add to basket) aren't copy-pasted inside test
bodies. Some helpers are pure-API; ``register_via_ui_then_login_via_api``
intentionally spans both layers to demonstrate a hybrid flow (a common
real-world pattern: seed state through whichever surface is faster/most
reliable, then verify through the other).
"""
from __future__ import annotations

from clients.rest_client import RestClient
from dao import auth_dao, basket_dao, product_dao, user_dao
from models.auth import Authentication
from models.user import NewUser
from pages.registration_page import RegistrationPage


def register_and_authenticate(client: RestClient, new_user: NewUser) -> Authentication:
    """Register ``new_user`` via the API, then log in and return the
    resulting authentication (token + basket id).

    Raises:
        ApiError: If registration or the follow-up login fails.
    """
    user_dao.register(
        client,
        new_user.email,
        new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    return auth_dao.authenticate(client, new_user.email, new_user.password)


def register_via_ui_then_login_via_api(
    registration_page: RegistrationPage,
    client: RestClient,
    new_user: NewUser,
) -> Authentication:
    """Register through the real UI form, then confirm the account works by
    logging in through the API — a hybrid check that the UI's registration
    flow produced a genuinely usable account.
    """
    registration_page.open()
    registration_page.register(new_user.email, new_user.password)
    return auth_dao.authenticate(client, new_user.email, new_user.password)


def add_first_search_result_to_basket(
    client: RestClient, token: str, basket_id: int, query: str
) -> int:
    """Search for ``query``, then add the first match to ``basket_id``.

    Returns:
        The id of the created basket item.

    Raises:
        ApiError: If the search or add-to-basket call fails.
        IndexError: If the search returned no products.
    """
    client.set_token(token)
    products = product_dao.search_products(client, query)
    return basket_dao.add_item(client, basket_id, products[0].id)
