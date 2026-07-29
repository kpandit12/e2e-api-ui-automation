# e2e-api-ui-automation

A layered, senior-grade Python test-automation framework that demonstrates
**API + UI automation** against the self-hosted [OWASP Juice
Shop](https://owasp.org/www-project-juice-shop/) app. It is built around the
same **4-layer architecture** used in production: **RestClient → DAO → Utility
→ Test**, with the UI layer mirroring that separation through **Page Object
Models**. The goal is not script-fragments but separation of concerns that
survive peer review.

---

## Architecture (4 + UI layers)

```text
Test  ────────────────  tests/api/**/*.py, tests/ui/e2e/*.py
                       thin, readable, intent-expressing
                       API tests never call requests; UI tests never use locators

Utility  ─────────────  utils/ecommerce_workflows.py
                        orchestration spanning DAO + Page Object calls
                        e.g. register_and_authenticate, add_first_search_result_to_basket

DAO / Page Objects  ──  dao/{auth,user,product,basket}_dao.py
                        pages/{login,registration,product,basket}_page.py
                        DAO: one function per API call, raises ApiError
                        Pages: one class per screen, hides selectors

RestClient / Browser  clients/rest_client.py  (single requests.Session owner)
                       pytest-playwright      (browser/context/page per test)
```

---

## Why each layer?

| Layer | Responsibility | Why separate it |
|-------|----------------|-----------------|
| **Test** | Assert user-visible behaviour | Keeps tests declarative; no HTTP plumbing, no page selectors. |
| **Utility** | Multi-step business operations | Reuses DAOs/Pages, handles setup/cleanup, keeps tests thin. |
| **DAO / Page Object** | One endpoint/screen, one abstraction | Centralises endpoint knowledge and error translation; easy to mock in unit tests. |
| **RestClient** | One owner of the HTTP session | Hides `requests`, retries, JWT auth, logging, and masking so every other layer speaks domain objects. |
| **Browser fixtures** | One owner of Playwright contexts | Gives every UI test an isolated browser context (cookies/storage) for parallel safety. |

---

## Running locally

### 1. Start the target app

Docker Desktop is required.

```bash
docker compose up -d
```

Wait for `http://localhost:3000` to load. The app is `bkimminich/juice-shop`.

### 2. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
pip install -r requirements-dev.txt
playwright install chromium
```

### 3. Optional environment overrides

```bash
cp .env.example .env
# QA_HEADLESS=false  # to watch the browser
# QA_BROWSER=firefox  # or webkit (defaults to chromium)
```

### 4. Run tests

```bash
pytest tests/api/unit -m unit                   # fast, offline
pytest tests/api/integration -m smoke -q        # minimal live API checks
pytest tests/api/integration -q                 # full API suite
pytest tests/api/contract -q                    # schema contract
pytest tests/ui/e2e -m smoke -q                 # browser smoke tests
pytest -q                                         # everything
```

For parallel execution (API tests only — keep UI serial):

```bash
pytest tests/api -m "not ui" -n auto
pytest tests/ui -m ui
```

Dev tooling:

```bash
ruff check . && mypy .
```

---

## CI/CD

The repo includes three equivalent options so you can pick what you already have.

### Option 1: Jenkins (`Jenkinsfile`)

A declarative `Jenkinsfile` is included in the repo root.

**What it does**

1. Builds a Python virtual environment and installs `requirements-dev.txt`.
2. Installs Chromium and Playwright system dependencies.
3. Starts Juice Shop with `docker compose up -d --wait`.
4. Runs `ruff`, `mypy`, API tests, and UI tests.
5. Publishes an Allure report and stops Juice Shop in `post { always }`.

**Agent requirements**

- Label: `docker && python` (change the `agent` block in `Jenkinsfile` to match your node labels).
- Internet access to Docker Hub and PyPI.
- Sudo/root access to install Playwright OS dependencies (`playwright install-deps chromium`).

**Creating the Jenkins job**

1. **Install Jenkins plugins** (Manage Jenkins → Plugins):
   - **Pipeline** (usually built-in)
   - **Allure Jenkins Plugin** (optional, for the Allure report)
   - **JUnit Plugin** (built-in on modern Jenkins)
2. **Prepare the Jenkins agent**:
   - Install Python 3.10+ and Docker.
   - Tag the agent with labels `docker` and `python` (or edit `agent { label 'docker && python' }` in the `Jenkinsfile`).
3. **Push this repo to Git** (GitHub/GitLab/Bitbucket). Jenkins reads the
   pipeline from source control, not your local working copy.
4. **New Item** → **Pipeline** → name it `e2e-api-ui-automation`.
5. Under **Pipeline**, choose **Pipeline script from SCM**:
   - **SCM**: Git
   - **Repository URL**: your repo URL
   - **Credentials**: add if the repo is private
   - **Branch Specifier**: `*/main` (or `*/master`)
   - **Script Path**: `Jenkinsfile`
6. Click **Save**.
7. Click **Build Now**. The first run may take a few minutes.
8. After the build finishes:
   - Open the build → **Console Output** for live logs.
   - If the Allure plugin is installed, click **Allure Report** for the report.

### Option 2: GitHub Actions (`.github/workflows/ci.yml`)

If you push the repo to GitHub, the workflow runs automatically on every push
and pull request to `main`/`master`. It splits the work into three jobs:

- `static-checks`: `ruff` + `mypy`
- `api-tests`: API unit/integration/contract tests
- `ui-tests`: UI E2E tests in headless Chromium

Juice Shop is provided as a service container on `localhost:3000` for each test
job. No Jenkins server needed.

### Option 3: Run locally as a CI simulation

If you don't have a CI server yet, use the helper scripts in `scripts/`.
They do exactly the same steps as the CI jobs.

Windows (PowerShell):

```powershell
.\scripts\run_ci_windows.ps1
```

Linux / macOS / WSL (bash):

```bash
chmod +x scripts/run_ci_linux.sh
./scripts/run_ci_linux.sh
```

Both scripts install dependencies, start Juice Shop, run all checks and tests,
and stop Juice Shop afterwards.

## Test pyramid

| Layer | Location | Hits network? | Count | What it covers |
|-------|----------|---------------|------:|----------------|
| Unit | `tests/api/unit` | No (mocked `responses`) | 43 | RestClient retries, token masking, DAO parsing, UserBuilder |
| API Integration | `tests/api/integration` | Yes | 14 | Registration, login, product search, basket CRUD, negative paths |
| Contract | `tests/api/contract` | Yes | 2 | Response shape vs pinned JSON Schema |
| UI E2E | `tests/ui/e2e` | Browser + backend | 8 | Registration, login, search, add-to-basket |

Total: **67** tests.

---

## Design decisions

- **Single `RestClient`** owns `requests.Session`, retry policy, JWT `Authorization`
  header, and structured logging. All HTTP traffic goes through it.
- **Functional DAO layer**: plain module functions (`login`, `register`,
  `search_products`, `add_item`) that take a `RestClient` and return typed models
  or raise `ApiError`.
- **Page Object Model**: each page class (`LoginPage`, `ProductPage`, …) owns its
  own locators and exposes intent methods (`login`, `search`, `add_to_basket_by_name`).
- **Thin exception subclasses with predicates**: `ApiError(status, body)` carries
  `.is_unauthorized()`, `.is_not_found()`, `.is_bad_request()`, etc.
- **Parallel safety**:
  - API: `UserBuilder.with_unique_email()` generates UUID-suffixed emails so
    concurrent `pytest-xdist` workers don't collide.
  - UI: `pytest-playwright` provides a fresh browser **context** per test.
- **Fixtures**:
  - API: function-scoped `client`; `registered_user` registers/logs in per test.
  - UI: function-scoped `page` with `login_page`, `product_page`, etc. injected
    from Page Object fixtures.

---

## Mutation testing

`mutmut` mutates `clients/`, `core/`, `dao/`, `utils/`, `models/`, `builders/`
and re-runs the unit suite. `pages/` is intentionally excluded because UI glue
is high-noise/low-signal for mutation testing.

```bash
mutmut run
mutmut results
```

Mutation score to be populated from the first full run.

---

## Known issues / first-run caveats

1. **Docker not installed in the original environment** — the test suite needs
   `docker compose up -d` running locally. The public demo instance can be used
   by overriding `QA_API_BASE_URL` and `QA_UI_BASE_URL`, but tests create/delete
   accounts and may interfere with each other on a shared demo.
2. **Page selectors are best-effort** — Juice Shop UI updates occasionally change
   Angular Material ids. If a UI test fails, inspect the page with Playwright's
   trace viewer (`--tracing retain-on-failure`) and update the locator in the
   relevant `pages/*.py` file.
3. **Juice Shop returns HTTP 500 for some invalid payloads** — the DAOs raise
   `ApiError` and tests assert on `.status` or `is_bad_request()`/`is_server_error()`
   according to observed live behaviour.
