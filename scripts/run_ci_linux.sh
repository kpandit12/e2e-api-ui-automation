#!/usr/bin/env bash
# Run the same checks and tests locally that the CI pipeline runs.
# This script is for Linux/macOS/WSL with Docker available.
set -euo pipefail

export QA_PROFILE=ci
export QA_API_BASE_URL=http://localhost:3000
export QA_UI_BASE_URL=http://localhost:3000
export QA_HEADLESS=true
export QA_BROWSER=chromium

cleanup() {
  echo "Stopping Juice Shop..."
  docker compose down --remove-orphans || true
}
trap cleanup EXIT

echo "Starting Juice Shop..."
docker compose up -d --wait

echo "Waiting for Juice Shop to be reachable..."
for i in $(seq 1 30); do
  curl -sf http://localhost:3000/rest/products/search?q=apple && break
  echo "  not ready yet..."
  sleep 2
done

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt

echo "Installing Playwright browser and dependencies..."
playwright install chromium
playwright install-deps chromium

echo "Running ruff..."
ruff check .

echo "Running mypy..."
mypy .

mkdir -p reports

echo "Running API tests..."
pytest tests/api/unit tests/api/integration tests/api/contract \
  -q --tb=short --alluredir=reports/allure-results --junitxml=reports/junit-api.xml \
  --cov=clients --cov=core --cov=dao --cov=utils --cov=builders --cov=models --cov=pages \
  --cov-report=term-missing --cov-report=xml:reports/coverage.xml

echo "Running UI tests..."
pytest tests/ui -q --tb=short \
  --tracing retain-on-failure --video retain-on-failure \
  --alluredir=reports/allure-results --junitxml=reports/junit-ui.xml

echo "All checks passed."
