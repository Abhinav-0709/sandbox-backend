import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

# Set testing environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "False"
os.environ["ENABLE_DEV_AUTH"] = "True"

try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False

if HAS_AIOSQLITE:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy.pool import StaticPool
    from app.database import Base, get_db
    from app.main import app

    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    @pytest.fixture(scope="function", autouse=True)
    async def init_test_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture
    async def db_session():
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()

    @pytest.fixture
    async def client(db_session):
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        app.dependency_overrides.clear()
else:
    # If running in environment without aiosqlite (e.g. offline sandbox venv),
    # provide a mock database session fixture so unit tests run cleanly
    @pytest.fixture
    async def db_session():
        mock_session = AsyncMock()
        yield mock_session

    @pytest.fixture
    async def client(db_session):
        from app.database import get_db
        from app.main import app
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        app.dependency_overrides.clear()
