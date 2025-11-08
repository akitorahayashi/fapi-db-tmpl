# FastAPI Database Template

A production-ready FastAPI template with Docker, PostgreSQL, and comprehensive testing.

## Features

- FastAPI framework
- Docker containerization
- PostgreSQL with Alembic migrations
- Pytest with testcontainers
- Code quality tools (Black, Ruff)
- Development commands via justfile

## Quick Start

### Setup

```bash
just setup
```

### Run

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
# Run all tests
just test

# Run database tests only
just test-db

# Run integration tests
just test-intg

# Run end-to-end tests
just test-e2e
```

#### Test Architecture

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Database Tests** (`tests/db/`): Test database operations with real PostgreSQL
- **Integration Tests** (`tests/intg/`): Test API endpoints with mocked dependencies
- **E2E Tests** (`tests/e2e/`): Test complete user workflows with full stack

When tests fail, container logs are automatically included in the failure report for debugging.

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
| `just format` | Format code |
| `just lint` | Lint code |
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