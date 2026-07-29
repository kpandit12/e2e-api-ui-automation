"""Unit-layer fixtures.

Unit tests exercise client/service *logic* (retries, error mapping, masking,
builders) against a mocked transport using the ``responses`` library, so they
run in milliseconds with no network. A ``NoRetryStrategy`` variant keeps
retry-free tests instant, while retry tests inject a fake ``sleep``.
"""
from __future__ import annotations

import pytest
import responses

from core.retry_strategy import NoRetryStrategy

BASE_URL = "https://api.test.local"


@pytest.fixture()
def mocked_responses():
    """Activate the ``responses`` mock for the duration of a test."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def no_retry() -> NoRetryStrategy:
    return NoRetryStrategy()
