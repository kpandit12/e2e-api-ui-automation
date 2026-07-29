"""Application configuration loaded from environment / .env file.

Nothing is hardcoded in the framework; every runtime value flows through this
Pydantic Settings object so it can be overridden per-environment. The
``local``, ``ci`` and ``unit`` profiles let the same code target different
environments (e.g. a mocked transport for unit tests, more patient retries in
CI) by setting ``PROFILE`` alone.

The target application under test is OWASP Juice Shop, self-hosted via
``docker-compose.yml`` (``bkimminich/juice-shop`` on ``localhost:3000``). The
same host serves both the REST API (``api_base_url``) and the Angular UI
(``ui_base_url``) — they default to the same value but are kept separate so a
future environment (e.g. a hosted demo instance with a different UI/API
split) can override just one.

``get_settings`` is memoised with :func:`functools.lru_cache`, giving a
process-scoped Singleton: the ``.env`` file is parsed exactly once and every
caller shares the same immutable instance.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Profile = Literal["local", "ci", "unit"]
Browser = Literal["chromium", "firefox", "webkit"]


class Settings(BaseSettings):
    """Strongly-typed settings sourced from environment variables / .env.

    Attributes:
        profile: Active environment profile; drives retry selection etc.
        api_base_url: Root URL of the Juice Shop REST API.
        ui_base_url: Root URL of the Juice Shop Angular UI.
        timeout: Per-request timeout in seconds.
        max_retries: Base number of attempts for the retry strategy.
        backoff_factor: Base backoff delay in seconds.
        browser: Playwright browser engine to drive.
        headless: Whether to run the browser without a visible window.
        seed_email: Email of the Juice Shop seeded admin account (useful for
            read-only checks); test-created accounts should prefer unique
            emails from ``builders.user_builder``.
        seed_password: Password of the seeded admin account.
    """

    profile: Profile = Field(default="local")
    api_base_url: str = Field(default="http://localhost:3000")
    ui_base_url: str = Field(default="http://localhost:3000")
    timeout: float = Field(default=30.0)
    max_retries: int = Field(default=3)
    backoff_factor: float = Field(default=0.5)
    browser: Browser = Field(default="chromium")
    headless: bool = Field(default=True)
    seed_email: str = Field(default="admin@juice-sh.op")
    seed_password: str = Field(default="admin123")

    model_config = SettingsConfigDict(
        env_prefix="QA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide Settings singleton (``.env`` parsed once)."""
    return Settings()
