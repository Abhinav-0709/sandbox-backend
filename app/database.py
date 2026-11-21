import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import text
from app.config import get_settings

settings = get_settings()

engine_kwargs = {
    "echo": settings.DEBUG and not settings.is_production and not settings.is_testing,
    "future": True,
}


def normalize_db_url(url: Optional[str]) -> str:
    """Normalize database URL for async SQLAlchemy / asyncpg / aiosqlite compatibility."""
    if not url:
        return "sqlite+aiosqlite:///./sandbox.db"
    clean_url = str(url).strip()
    if clean_url.startswith("postgres://"):
        clean_url = clean_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif clean_url.startswith("postgresql://") and "+asyncpg" not in clean_url:
        clean_url = clean_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif clean_url.startswith("sqlite://") and "+aiosqlite" not in clean_url:
        clean_url = clean_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # asyncpg expects ssl= rather than sslmode=
    if "sslmode=" in clean_url:
        clean_url = clean_url.replace("sslmode=", "ssl=")
    return clean_url


db_url = normalize_db_url(settings.DATABASE_URL)
if "sqlite" in db_url:
    engine_kwargs["poolclass"] = StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL (asyncpg with pgbouncer transaction pooler compatibility)
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,  # Required for PgBouncer / Supabase transaction poolers
    }

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Common alias for compatibility across scripts and test helpers
async_session_factory = AsyncSessionLocal


class Base(DeclarativeBase):
    """Base model for all Sandbox entities."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if session.is_active:
                await session.commit()
        except Exception:
            if session.is_active:
                await session.rollback()
            raise


async def check_db_health(timeout: float = 3.0) -> bool:
    """Check database connectivity with timeout protection."""
    try:
        async def _ping():
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        await asyncio.wait_for(_ping(), timeout=timeout)
        return True
    except Exception:
        return False
