# FastAPI Database Template

A production-ready FastAPI template with Docker, PostgreSQL, and comprehensive testing.

## Features

- FastAPI framework
- Docker containerization
- PostgreSQL with Alembic migrations
- Pytest with testcontainers
- Code quality tools (Ruff, Mypy)
- Development commands via justfile

## Quick Start

### Setup

```bash
just setup
```

### Run (Docker Development Stack)

```bash
just up
```

API available at `http://127.0.0.1:8000`

### Testing

This project uses advanced testcontainers features for reliable, isolated testing:

#### Test Setup

- **Docker Compose Integration**: Tests run against real PostgreSQL and API containers
- **Robust Wait Strategies**: Uses `LogMessageWaitStrategy` to wait for database migrations completion
- **Clean Dependency Injection**: Database connections are passed directly to test fixtures without environment pollution
- **Automatic Debug Logging**: Failed tests automatically include container logs for easier troubleshooting

#### Running Tests

```bash
# Run all tests (local + dockerized)
just test

# Local tests (no Docker)
just local-test   # unit + db (SQLite) + intg
just unit-test    # unit tests only
just sqlt-test    # database tests with SQLite
just intg-test    # API integration tests (in-process FastAPI)

# Docker-based tests (PostgreSQL + containers)
just docker-test  # api-test + e2e-test
just api-test     # dockerized API tests (development target)
just e2e-test     # production-like E2E tests (PostgreSQL)
```

#### Test Architecture

- **Unit Tests** (`tests/unit/`): Test individual components in isolation.
- **Database Tests** (`tests/db/`): Test database operations; run with SQLite by default, and PostgreSQL under Docker.
- **Integration Tests** (`tests/intg/`): Test API endpoints with DI overrides using in-process FastAPI and ASGITransport.
- **E2E Tests** (`tests/e2e/`): Test complete user workflows against dockerized API + PostgreSQL.

## API Endpoints

- `GET /health` - Health check
- `GET /greetings/{name}` - Personalized greeting

## Development Commands

| Command | Description |
|---------|-------------|
| `just setup` | Initialize environment |
| `just up` | Start development containers |
| `just down` | Stop containers |
| `just test` | Run all tests |
| `just fix` | Format code |
| `just check` | Lint code |
| `just rebuild` | Rebuild API container |

## Project Structure

```
src/fapi_db_tmpl/
├── api/          # API routes and services
├── config/       # Configuration
├── db/           # Database models
└── main.py       # Application entry

tests/            # Comprehensive test suite
├── unit/         # Unit tests
├── db/           # Database integration tests
├── intg/         # Integration tests
└── e2e/          # End-to-end tests

alembic/          # Database migrations
```

## Environment Variables

Key variables in `.env`:

- `FAPI_DB_TMPL_HOST_PORT` - API port (default: 8000)
- `POSTGRES_*` - Database configuration
- `FAPI_DB_TMPL_USE_MOCK_GREETING` - Use mock service (default: false)
