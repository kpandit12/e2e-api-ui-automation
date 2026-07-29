"""Contract tests: guard the provider response *shape* against a schema.

Unlike the integration tests (which assert behaviour), these fail loudly the
moment Juice Shop changes its response shape, independent of whether the
specific values under test are otherwise correct.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import pytest

from builders.user_builder import UserBuilder
from clients.rest_client import RestClient
from dao import auth_dao, user_dao

SCHEMAS_DIR = Path(__file__).parents[3] / "data" / "schemas"


def _schema(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((SCHEMAS_DIR / name).read_text()))


@pytest.mark.contract
def test_product_search_response_matches_schema(client: RestClient) -> None:
    response = client.get("/rest/products/search", params={"q": "apple"})
    jsonschema.validate(response.json, _schema("product_search_schema.json"))


@pytest.mark.contract
def test_login_response_matches_schema(client: RestClient) -> None:
    new_user = UserBuilder().build()
    user_dao.register(
        client, new_user.email, new_user.password,
        password_repeat=new_user.passwordRepeat,
    )
    response = auth_dao.login_response(client, new_user.email, new_user.password)
    jsonschema.validate(response.json, _schema("login_schema.json"))
