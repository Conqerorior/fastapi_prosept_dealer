import asyncio
from datetime import datetime
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import (DB_TEST_HOST, DB_TEST_NAME, DB_TEST_PASSWORD,
                        DB_TEST_PORT, DB_TEST_USER)
from app.db.database import Base, get_db
from app.main import app
from app.products.models import MarketingDealerPrice, MarketingProduct

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


@pytest.fixture(scope='session')
async def fixture_marketing_dealer_price():
    async with async_session_marker() as session:
        test_data = insert(MarketingDealerPrice).values(
            id=1,
            product_key='1234567890',
            price=1000,
            product_url='https://example.com/product1',
            product_name='Продукт 1',
            date=datetime.now(),
            dealer_id=1
        )
        await session.execute(test_data)
        await session.commit()

    return MarketingDealerPrice


@pytest.fixture(scope='session')
async def fixture_marketing_products():
    async with async_session_marker() as session:
        for i in range(1, 6):
            test_data = insert(MarketingProduct).values(
                id=i,
                article=f'Артикул {i * 5}',
                ean_13=f'EAN-13 {i * 10}',
                name=f'Продукт {i}',
                cost=10 * i,
                recommended_price=150 * i,
                category_id='Категория',
                ozon_name=f'Название на Озоне {i}',
                name_1c=f'Название в 1C {i}',
                wb_name=f'Название на Wildberries {i}',
                ozon_article=f'Описание для Озон {i}',
                wb_article=f'Артикул для Wildberries {i}',
                ym_article=f'Артикул для Яндекс.Маркета {i}',
                wb_article_td=f'Артикул для Wildberries td {i}'
            )
            await session.execute(test_data)
            await session.commit()

    return MarketingProduct
