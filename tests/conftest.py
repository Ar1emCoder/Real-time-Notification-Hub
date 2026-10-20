import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.models import User

TEST_DATABASE_URL = "postgresql+asyncpg://notification_user:change_me_in_production@localhost:5432/test_db"

@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# -------------------------
@pytest_asyncio.fixture(scope="function")
async def test_user_chat_id(async_session):
    user = User(telegram_chat_id="test_chat_123", timezone="UTC")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)  # Чтобы убедиться, что он точно в БД

    return user.telegram_chat_id