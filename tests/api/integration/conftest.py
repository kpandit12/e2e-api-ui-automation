"""API integration-layer fixtures (hit the real Juice Shop API).

``settings``/``client`` live in the root ``tests/conftest.py`` (shared with
the contract layer). This module adds a ``registered_user`` fixture: a fresh
account + authenticated session, created per test for parallel safety
(pytest-xdist) since every test gets its own unique email/basket.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import NamedTuple

import pytest

from builders.user_builder import UserBuilder
from clients.rest_client import RestClient
from dao import auth_dao, user_dao
from models.user import NewUser


class RegisteredUser(NamedTuple):
    """A freshly registered + logged-in account, ready to use in a test."""

    new_user: NewUser
    token: str
    basket_id: int | None


@pytest.fixture()
def new_user() -> NewUser:
    """A unique, valid registration payload (override via UserBuilder in-test
    for negative cases).
    """
    return UserBuilder().build()


@pytest.fixture()
def registered_user(
    client: RestClient, new_user: NewUser
) -> Iterator[RegisteredUser]:
    """Register ``new_user`` via the API and log in, attaching the token to
    ``client`` so DAO calls made with it are authenticated automatically.
    """
    user_dao.register(
        client, new_user.email, new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    auth = auth_dao.authenticate(client, new_user.email, new_user.password)
    client.set_token(auth.token)
    yield RegisteredUser(new_user=new_user, token=auth.token, basket_id=auth.bid)
