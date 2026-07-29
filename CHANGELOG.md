# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **API + UI automation framework** targeting OWASP Juice Shop.
  - `dao/` — functional API wrappers: `auth_dao`, `user_dao`, `product_dao`,
    `basket_dao`, each raising `ApiError` with `.is_*` predicates.
  - `models/` — Pydantic models for `Authentication`, `User`, `Product`, `BasketItem`.
  - `pages/` — Playwright Page Object Models: `BasePage`, `LoginPage`,
    `RegistrationPage`, `ProductPage`, `BasketPage`.
  - `builders/user_builder.py` — fluent builder with unique UUID emails for parallel
    safety.
  - `utils/ecommerce_workflows.py` — orchestration (`register_and_authenticate`,
    `add_first_search_result_to_basket`).
  - `tests/api/{unit,integration,contract}/` — API unit/integration/contract tests.
  - `tests/ui/e2e/` — Playwright end-to-end tests for registration, login, search,
    and add-to-basket.
  - `docker-compose.yml` — single-container `bkimminich/juice-shop` setup.

### Changed
- Renamed project identity to `e2e-api-ui-automation` in `pyproject.toml`.
- `config/settings.py` now exposes `api_base_url`, `ui_base_url`, `browser`,
  `headless`, and `seed_*` credentials with `QA_` env prefix.
- `clients/rest_client.py` switched auth header to `Authorization: Bearer <JWT>`
  for Juice Shop's login shape.
- `.env.example`, `.pre-commit-config.yaml`, and README/CHANGELOG updated for the
  new target, new directory layout, and Playwright setup instructions.

### Removed
- All restful-booker-specific artefacts: `dao/booking_dao.py`, `dao/ping_dao.py`,
  `models/booking.py`, `builders/booking_builder.py`, `utils/booking_workflows.py`,
  `data/parametrized_bookings.json`, and all old booking-only tests.
- The `factories/` package and `services/` package (already removed earlier).

## [1.0.1] - 2026-07-20

### Changed
- Refactored the restful-booker framework into the 4-layer production architecture:
  `clients/rest_client.py`, `dao/` package, `utils/`, `tests/`.
- Introduced `ApiError` with `.is_*` predicates and thin subclasses.
- Fixed `Settings` OS `USERNAME` collision with `RB_` env prefix.
- Updated README, CHANGELOG, and mutation testing scope.

## [1.0.0] - 2026-07-16

### Added
- Initial restful-booker Python API automation framework.

