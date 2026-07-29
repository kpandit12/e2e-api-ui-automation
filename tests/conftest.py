"""Root test configuration shared by all pyramid layers.

Logging is configured once here so every test emits structured, correlatable
lines. ``settings``/``client`` live here (rather than in
``tests/api/integration/conftest.py``) because both the API integration *and*
contract layers hit the live Juice Shop API and need the same session-scoped
``RestClient`` without duplicating the wiring. Most tests register their own
unique account (see ``builders.user_builder.UserBuilder``) rather than
sharing a logged-in session, since Juice Shop ties baskets/orders to the
account, not a fixed admin login.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

import pytest

from clients.rest_client import RestClient, build_rest_client
from config.settings import get_settings
from core.logging_config import configure_logging, set_request_id

configure_logging(logging.INFO)


@pytest.fixture(autouse=True)
def _correlation_id(request: pytest.FixtureRequest) -> None:
    """Bind a per-test correlation id so client logs trace back to the test."""
    set_request_id(request.node.name)


@pytest.fixture(scope="session")
def settings() -> Any:
    """The resolved configuration for the run."""
    return get_settings()


@pytest.fixture()
def client(settings: Any) -> Iterator[RestClient]:
    """A fresh, unauthenticated RestClient for the Juice Shop API.

    Function-scoped (not session-scoped): most tests log in as their own
    freshly-registered account via ``auth_dao.authenticate``/``login``, so
    sharing one client across the session would leak tokens between tests.
    """
    rest = build_rest_client(settings)
    yield rest
    rest.close()
