"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from backend.core.config import Settings, get_settings
from backend.db.base import Base, get_db
from backend.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/codorch_test"


def get_test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        ENVIRONMENT="test",
        DATABASE_URL=TEST_DATABASE_URL,
        OPENAI_API_KEY="test_api_key",
        JWT_SECRET_KEY="test-secret-key",
        DEBUG=True,
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback() # Rollback after each test
        await session.close()


@pytest.fixture(scope="function")
def client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """Create test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = get_test_settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_ai_client() -> MagicMock:
    """Mock AI client for testing."""
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test AI response"))]
    )
    return mock


@pytest.fixture
def sample_user_data() -> Dict[str, str]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_project_data() -> Dict[str, str]:
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "goal": "Build an awesome application",
    }
