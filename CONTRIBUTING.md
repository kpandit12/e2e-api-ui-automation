# Contributing

Thanks for improving this framework. This guide keeps changes reviewable and
the history readable.

## Local setup

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pre-commit install
```

## Branch naming

Use `type/short-description`, matching the Conventional Commit type:

- `feat/add-basket-workflow`
- `fix/retry-backoff-off-by-one`
- `chore/bump-pytest`
- `docs/readme-design-decisions`
- `test/add-idor-coverage`

## Commit messages — Conventional Commits

```
<type>(<optional scope>): <imperative summary>

<optional body explaining what/why>
<optional footer, e.g. BREAKING CHANGE: ...>
```

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`,
`ci`, `chore`. Examples:

- `feat(utils): add register_and_authenticate workflow`
- `fix(core): grow backoff exponentially instead of linearly`
- `test(security): add IDOR probe for unauthenticated PUT`

## Before you push

Pre-commit runs these automatically, but you can run them by hand:

```bash
ruff check . && ruff format --check .
mypy .
pytest tests/unit -q          # fast, offline
```

## Pull request checklist

- [ ] Title follows Conventional Commits.
- [ ] `ruff check` and `ruff format --check` pass.
- [ ] `mypy` (strict) passes on framework source.
- [ ] New/changed behaviour is covered by tests in the right pyramid layer
      (`unit` for client/service logic, `integration` for live API, `contract`
      for response shape).
- [ ] Tests that touch the shared public API create and delete their own data
      (parallel-safe) — no shared fixtures mutated across tests.
- [ ] No secrets committed; `.env` stays local, only `.env.example` is tracked.
- [ ] `CHANGELOG.md` updated under `Unreleased`.
- [ ] Known-flaky/network tests are tagged (`@pytest.mark.flaky`) rather than
      silently retried.
