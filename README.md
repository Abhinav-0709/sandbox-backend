# Vivoki Sandbox Platform — Backend Microservice

Independent microservice providing environment orchestration, sandbox session lifecycles, real-time activity telemetry ingestion, anti-cheat detection, and deterministic & rubric-based scoring.

## Architecture

- **Framework**: FastAPI (async Python 3.11+)
- **Database**: PostgreSQL (Supabase) via SQLAlchemy 2.0 Async (asyncpg)
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio, httpx
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`)

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e .[dev]

# 3. Start development server
uvicorn app.main:app --reload --port 8001
```

## Running Tests

```bash
pytest tests/ -v
```
