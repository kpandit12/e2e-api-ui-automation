"""UI Layer — Page Object Models (Playwright).

Each page exposes intent-revealing methods (``login_page.login(email, pw)``)
instead of leaking locators into tests, mirroring how the DAO layer hides
HTTP details from the API tests. Locators here target OWASP Juice Shop
(self-hosted via ``docker-compose.yml``); verify them against a running
instance if the app version changes (``docker run -p 3000:3000
bkimminich/juice-shop``).
"""
