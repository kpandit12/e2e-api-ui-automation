"""Unit tests for token masking in the request logger."""
import pytest

from core.request_logger import mask_headers, mask_value


@pytest.mark.unit
def test_bearer_token_is_masked_but_scheme_kept() -> None:
    assert mask_value("Bearer abc.def.ghi") == "Bearer ***MASKED***"


@pytest.mark.unit
def test_raw_token_value_is_fully_masked() -> None:
    assert mask_value("abcdef123456") == "***MASKED***"


@pytest.mark.unit
def test_headers_authorization_and_cookie_are_masked() -> None:
    headers = {
        "Authorization": "Bearer secret",
        "Cookie": "token=supersecret",
        "Content-Type": "application/json",
    }
    masked = mask_headers(headers)
    assert masked["Authorization"] == "Bearer ***MASKED***"
    assert masked["Cookie"] == "***MASKED***"
    assert masked["Content-Type"] == "application/json"  # untouched


@pytest.mark.unit
def test_masking_does_not_mutate_input() -> None:
    headers = {"Authorization": "Bearer secret"}
    mask_headers(headers)
    assert headers["Authorization"] == "Bearer secret"
