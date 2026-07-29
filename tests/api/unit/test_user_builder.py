"""Unit tests for the UserBuilder."""

import pytest

from builders.user_builder import UserBuilder


@pytest.mark.unit
def test_default_build_has_valid_unique_email_and_matching_passwords() -> None:
    user = UserBuilder().build()
    assert "@" in user.email
    assert user.password == user.passwordRepeat


@pytest.mark.unit
def test_two_default_builds_get_different_emails() -> None:
    assert UserBuilder().build().email != UserBuilder().build().email


@pytest.mark.unit
def test_with_email_overrides_default() -> None:
    user = UserBuilder().with_email("fixed@test.local").build()
    assert user.email == "fixed@test.local"


@pytest.mark.unit
def test_with_mismatched_repeat_produces_divergent_passwords() -> None:
    user = (
        UserBuilder().with_password("pw12345").with_mismatched_repeat("other").build()
    )
    assert user.password != user.passwordRepeat
