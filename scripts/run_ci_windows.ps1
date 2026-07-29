# Run the same checks and tests locally that the CI pipeline runs.
# This script is for Windows with Docker Desktop / docker engine available.
$ErrorActionPreference = "Stop"

$env:QA_PROFILE = "ci"
$env:QA_API_BASE_URL = "http://localhost:3000"
$env:QA_UI_BASE_URL = "http://localhost:3000"
$env:QA_HEADLESS = "true"
$env:QA_BROWSER = "chromium"

Write-Host "Starting Juice Shop..."
docker compose up -d --wait

try {
    Write-Host "Waiting for Juice Shop to be reachable..."
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:3000/rest/products/search?q=apple" -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $ready = $true
                break
            }
        } catch {
            Write-Host "  not ready yet..."
        }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) {
        throw "Juice Shop did not become reachable"
    }

    Write-Host "Creating virtual environment..."
    python -m venv .venv
    . .venv\Scripts\Activate.ps1

    Write-Host "Installing dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements-dev.txt

    Write-Host "Installing Playwright browser and dependencies..."
    playwright install chromium
    playwright install-deps chromium

    Write-Host "Running ruff..."
    ruff check .

    Write-Host "Running mypy..."
    mypy .

    New-Item -ItemType Directory -Path "reports" -ErrorAction SilentlyContinue | Out-Null

    Write-Host "Running API tests..."
    pytest tests/api/unit tests/api/integration tests/api/contract `
      -q --tb=short --alluredir=reports/allure-results --junitxml=reports/junit-api.xml `
      --cov=clients --cov=core --cov=dao --cov=utils --cov=builders --cov=models --cov=pages `
      --cov-report=term-missing --cov-report=xml:reports/coverage.xml

    Write-Host "Running UI tests..."
    pytest tests/ui -q --tb=short `
      --tracing retain-on-failure --video retain-on-failure `
      --alluredir=reports/allure-results --junitxml=reports/junit-ui.xml

    Write-Host "All checks passed."
} finally {
    Write-Host "Stopping Juice Shop..."
    docker compose down --remove-orphans
}
