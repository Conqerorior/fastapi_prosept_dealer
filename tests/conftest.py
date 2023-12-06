import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import (DB_TEST_HOST, DB_TEST_NAME, DB_TEST_PASSWORD,
                         DB_TEST_PORT, DB_TEST_USER)
from app.db.database import get_db, Base
from app.main import app


SQLALCHEMY_DATABASE_URL_TEST = (
    f"postgresql+asyncpg:"
    f"//{DB_TEST_USER}"
    f":{DB_TEST_PASSWORD}"
    f"@{DB_TEST_HOST}"
    f":{DB_TEST_PORT}"
    f"/{DB_TEST_NAME}"
)


engine_test = create_async_engine(SQLALCHEMY_DATABASE_URL_TEST,
                                  poolclass=NullPool)
async_session_marker = sessionmaker(engine_test,
                                    class_=AsyncSession,
                                    expire_on_commit=False)

Base.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_marker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_async_session()


@pytest.fixture(autouse=True, scope='session')
async def create_db():
    """Создание Таблиц в Базе Данных."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def custom_event_loop(request):
    """Создание экземпляра цикла событий по умолчанию
     для каждого тестового примера."""
    loop = asyncio.set_event_loop(asyncio.new_event_loop())

    yield loop


@pytest.fixture(scope='session')
async def async_client(custom_event_loop) -> AsyncGenerator[AsyncClient, None]:
    """Создание Асинхронного Клиента."""
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
