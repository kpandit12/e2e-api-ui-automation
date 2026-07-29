/* groovylint-disable-next-line CompileStatic */
pipeline {
    agent {
        // This pipeline expects a Linux agent that has:
        //   - Python 3.10+ and pip
        //   - Docker / docker compose
        //   - Internet access to Docker Hub and PyPI
        // For Playwright system deps the agent needs apt or equivalent.
        label 'docker && python'
    }

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        // Force CI profile so retry/backoff settings match a remote target.
        QA_PROFILE = 'ci'
        QA_API_BASE_URL = 'http://localhost:3000'
        QA_UI_BASE_URL = 'http://localhost:3000'
        QA_HEADLESS = 'true'
        QA_BROWSER = 'chromium'
        // Avoid collisions when multiple jobs run on the same agent.
        COMPOSE_PROJECT_NAME = "juice-shop-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build venv') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Install Playwright browser & deps') {
            steps {
                sh '''
                    . .venv/bin/activate
                    playwright install ${QA_BROWSER}
                    playwright install-deps ${QA_BROWSER}
                '''
            }
        }

        stage('Start Juice Shop') {
            steps {
                sh '''
                    docker compose up -d --wait
                    # Extra sanity check: the --wait above waits for healthy status,
                    # but the first request can still be slow while Node warms up.
                    for i in $(seq 1 30); do
                        curl -sf http://localhost:3000/rest/products/search?q=apple && break
                        echo "Waiting for Juice Shop to respond..."
                        sleep 2
                    done
                '''
            }
        }

        stage('Static checks') {
            steps {
                sh '''
                    . .venv/bin/activate
                    ruff check .
                    mypy .
                '''
            }
        }

        stage('API tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest tests/api/unit tests/api/integration tests/api/contract \
                        -q --tb=short --alluredir=reports/allure-results
                '''
            }
        }

        stage('UI tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest tests/ui -q --tb=short --alluredir=reports/allure-results
                '''
            }
        }
    }

    post {
        always {
            // Always stop the target container so the agent is left clean.
            sh 'docker compose down --remove-orphans || true'

            // Publish the Allure report if the Jenkins Allure plugin is installed.
            allure(
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'reports/allure-results']]
            )

            // Keep JUnit-style XML available even without the Allure plugin.
            junit(
                allowEmptyResults: true,
                testResults: 'reports/*.xml'
            )
        }
    }
}
