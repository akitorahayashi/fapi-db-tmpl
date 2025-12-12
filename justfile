# ==============================================================================
# justfile for FastAPI Project Automation
# ==============================================================================

set dotenv-load

PROJECT_NAME := env("FAPI_DB_TMPL_PROJECT_NAME", "fapi-db-tmpl")
POSTGRES_IMAGE := env("POSTGRES_IMAGE", "postgres:16-alpine")

DEV_PROJECT_NAME := PROJECT_NAME + "-dev"
PROD_PROJECT_NAME := PROJECT_NAME + "-prod"

DEV_COMPOSE  := "docker compose -f docker-compose.yml --project-name " + DEV_PROJECT_NAME
PROD_COMPOSE := "docker compose -f docker-compose.yml --project-name " + PROD_PROJECT_NAME

# default target
default: help

# Show available recipes
help:
    @echo "Usage: just [recipe]"
    @echo "Available recipes:"
    @just --list | tail -n +2 | awk '{printf "  \033[36m%-20s\033[0m %s\n", $1, substr($0, index($0, $2))}'
# ==============================================================================
# Environment Setup
# ==============================================================================

# Initialize project: install dependencies, create .env file and pull required Docker images
setup:
    @echo "Installing python dependencies with uv..."
    @uv sync
    @echo "Creating environment file..."
    @if [ ! -f .env ] && [ -f .env.example ]; then \
        echo "Creating .env from .env.example..."; \
        cp .env.example .env; \
        echo "✅ Environment file created (.env)"; \
    else \
        echo ".env already exists. Skipping creation."; \
    fi
    @echo "💡 You can customize .env for your specific needs:"
    @echo "   📝 Change OLLAMA_HOST to switch between container/host Ollama"
    @echo "   📝 Adjust other settings as needed"
    @echo ""
    @echo "Pulling PostgreSQL image for tests..."
    docker pull {{POSTGRES_IMAGE}}
    @echo "✅ Setup complete. Dependencies are installed and .env file is ready."

# ==============================================================================
# Development Environment Commands
# ==============================================================================

# Start all development containers in detached mode (development target)
up:
    @echo "Starting up development services..."
    @FAPI_DB_TMPL_BUILD_TARGET=development {{DEV_COMPOSE}} up -d

# Stop and remove all development containers
down:
    @echo "Shutting down development services..."
    @{{DEV_COMPOSE}} down --remove-orphans

# Rebuild and restart API container only (development target)
rebuild:
    @echo "Rebuilding and restarting API service..."
    @{{DEV_COMPOSE}} down --remove-orphans
    @FAPI_DB_TMPL_BUILD_TARGET=development {{DEV_COMPOSE}} build --no-cache fapi-db-tmpl
    @FAPI_DB_TMPL_BUILD_TARGET=development {{DEV_COMPOSE}} up -d

# Start production stack (production target)
up-prod:
    @echo "Starting production stack..."
    @FAPI_DB_TMPL_BUILD_TARGET=production {{PROD_COMPOSE}} up -d

# Stop production stack
down-prod:
    @echo "Stopping production stack..."
    @{{PROD_COMPOSE}} down --remove-orphans

# Rebuild and restart production stack
rebuild-prod:
    @echo "Rebuilding production stack..."
    @{{PROD_COMPOSE}} down --remove-orphans
    @FAPI_DB_TMPL_BUILD_TARGET=production {{PROD_COMPOSE}} build --no-cache fapi-db-tmpl
    @FAPI_DB_TMPL_BUILD_TARGET=production {{PROD_COMPOSE}} up -d

# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Automatically format and fix code (Ruff)
fix:
    @echo "🔧 Formatting and fixing code..."
    @uv run ruff format .
    @uv run ruff check . --fix

# Run static checks (Ruff, Mypy)
check:
    @echo "🔍 Running static checks..."
    @uv run ruff format --check .
    @uv run ruff check .
    @uv run mypy --explicit-package-bases src

# ==============================================================================
# TESTING
# ==============================================================================

# Run complete test suite
test:
    @just local-test
    @just docker-test

# Run lightweight local (in-process) test suite
local-test:
    @just unit-test
    @just sqlt-test
    @just intg-test

# Run unit tests locally
unit-test:
    @echo "🚀 Running unit tests..."
    @uv run pytest tests/unit

# Run database tests with SQLite (in-process DB)
sqlt-test:
    @echo "🚀 Running database tests with SQLite..."
    @FAPI_DB_TMPL_USE_SQLITE=true uv run pytest tests/db

# Run integration tests locally (in-process FastAPI + DB overrides)
intg-test:
    @echo "🚀 Running integration tests..."
    @uv run pytest tests/intg

# Run all Docker-based tests
docker-test:
    @just api-test
    @just e2e-test

# Run dockerized API tests against development target (PostgreSQL)
api-test:
    @echo "🚀 Building image for dockerized API tests (development target, PostgreSQL)..."
    @docker build --target development -t fapi-db-tmpl-e2e:dev .
    @echo "🚀 Running dockerized API tests (development target, PostgreSQL)..."
    @FAPI_DB_TMPL_E2E_IMAGE=fapi-db-tmpl-e2e:dev FAPI_DB_TMPL_USE_SQLITE=false FAPI_DB_TMPL_BUILD_TARGET=development FAPI_DB_TMPL_HOST_PORT=0 uv run pytest tests/e2e

# Run e2e tests against production-like target (PostgreSQL)
e2e-test:
    @echo "🚀 Building image for production acceptance tests (PostgreSQL)..."
    @docker build --target production -t fapi-db-tmpl-e2e:prod .
    @echo "🚀 Running production acceptance tests (PostgreSQL)..."
    @FAPI_DB_TMPL_E2E_IMAGE=fapi-db-tmpl-e2e:prod FAPI_DB_TMPL_USE_SQLITE=false FAPI_DB_TMPL_BUILD_TARGET=production FAPI_DB_TMPL_HOST_PORT=0 uv run pytest tests/e2e

# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and .venv to make project lightweight
clean:
    @echo "🧹 Cleaning up project..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @rm -rf .uv-cache
    @rm -f test_db.sqlite3
    @echo "✅ Cleanup completed"
