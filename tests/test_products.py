from datetime import datetime
from urllib.parse import urlparse

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import async_session_marker
from app.products.models import (MarketingDealer,
                                 MarketingDealerPrice,
                                 MarketingProduct, MarketingProductDealerKey)


async def data_to_dict(obj):
    """Преобразование объектов в список словарей."""

    result = [
        {c.name: getattr(md, c.name) for c in md.__table__.columns} for md
        in obj]
    return result


async def compare_type(must, expected):
    """Проверка на тип данных"""

    for key, expected_type in expected.items():
        assert isinstance(must[0][key],
                          expected_type), f"Неверный тип данных для {key}"
    return True


async def test_marketing_dealer(async_client: AsyncClient):
    """Создаем тестовую запись в базе данных."""

    async with async_session_marker() as session:
        test_data = insert(MarketingDealer).values(
            id=1,
            name='Test_Dealer'
        )
        await session.execute(test_data)
        await session.commit()

        query = select(MarketingDealer)
        res = await session.execute(query)
        marketing_dealers = res.scalars().all()

        result = await data_to_dict(marketing_dealers)

        assert result is not None
        assert len(result[0]) == 2
        assert result[0]['id'] == 1
        assert result[0]['name'] == 'Test_Dealer'


async def test_marketing_dealer_price(
        fixture_marketing_dealer_price: MarketingDealerPrice):

    async with async_session_marker() as session:
        query = select(MarketingDealerPrice)
        res = await session.execute(query)
        marketing_dealer_price = res.scalars().all()
        result = await data_to_dict(marketing_dealer_price)

        expected_data = [{
            'id': 1,
            'product_key': '1234567890',
            'price': 1000.0,
            'product_url': 'https://example.com/product1',
            'product_name': 'Продукт 1',
            'date': result[0]['date'],
            'dealer_id': 1
        }]

        result_db = await session.execute(
            select(MarketingDealerPrice).filter_by(id=1))

        parsed_url = urlparse(result[0]['product_url'])

        expected_types = {
            'id': int,
            'product_key': str,
            'price': float,
            'product_url': str,
            'product_name': str,
            'date': datetime,
            'dealer_id': int
        }

        exp_type = await compare_type(result, expected_types)

        assert exp_type
        assert len(result) == 1, "Ожидается только одна запись"
        assert result == expected_data, 'Данные не соответствуют'
        assert result_db.scalar() is not None, "Запись не найдена в базе данных"
        assert parsed_url.scheme and parsed_url.netloc, "Неверный формат URL"
        assert result[0]['product_key'] is not None, "product_key None"
        assert result[0]['price'] > 0, "Цена должна быть положительной"


async def test_marketing_product(
        fixture_marketing_products: MarketingProduct):

    async with async_session_marker() as session:
        query = select(MarketingProduct)
        res = await session.execute(query)
        marketing_product = res.scalars().all()
        result = await data_to_dict(marketing_product)
        print(result)
        print(result)
        print(result)
#
#         expected_data = [{
#             'id': 1,
#             'article': '123-02',
#             'ean_13': '4610093420560.0',
#             'cost': 189,
#             'name': 'Средство для удаления наклеек Duty Universal / 210мл',
#             'recommended_price': 443,
#             'category_id': '43.0',
#             'ozon_name': 'Средство для удаления клейкой ленты, клея, наклеек PROSEPT "Duty Universal", 0.2 л.',
#             'name_1c': 'Средство для удаления клейкой ленты, клея, наклеек PROSEPT "Duty Universal", 0.2 л.',
#             'wb_name': 'Средство для удаления клейкой ленты, клея, наклеек PROSEPT "Duty Universal", 0.2 л.',
#             'ozon_article': '445949007.0',
#             'wb_article': '189522705.0',
#             'ym_article': '150033482.0',
#             'wb_article_td': '008-1'
#         }]
#
#         result_db = await session.execute(
#             select(MarketingDealerPrice).filter_by(id=1))
#
#         expected_types = {
#             'id': int,
#             'article': str,
#             'ean_13': str,
#             'cost': float,
#             'name': str,
#             'recommended_price': float,
#             'category_id': str,
#             'ozon_name': str,
#             'name_1c': str,
#             'wb_name': str,
#             'ozon_article': str,
#             'wb_article': str,
#             'ym_article': str,
#             'wb_article_td': str
#         }
#
#         exp_type = await compare_type(result, expected_types)
#
#         assert exp_type
#         assert len(result) == 1, "Ожидается только одна запись"
#         assert result == expected_data, 'Данные не соответствуют'
#         assert result_db.scalar() is not None, "Запись не найдена в базе данных"
#
#
# async def test_product_dealer_key():
#     async with async_session_marker() as session:
#         # test_data = insert(MarketingProductDealerKey).values(
#         #     id=1,
#         #     key='546227',
#         #     product_id=1,
#         #     dealer_id=1,
#         # )
#         #
#         # await session.execute(test_data)
#         # await session.commit()
#
#         query = select(MarketingProductDealerKey)
#         res = await session.execute(query)
#         marketing_product = res.scalars().all()
#         result = await data_to_dict(marketing_product)
#
#         expected_data = [{
#             'id': 1,
#             'key': '546227',
#             'product_id': 1,
#             'dealer_id': 1,
#         }]
#
#         result_db = await session.execute(
#             select(MarketingDealerPrice).filter_by(id=1))
#
#         expected_types = {
#             'id': int,
#             'key': str,
#             'product_id': int,
#             'dealer_id': int,
#         }
#
#         exp_type = await compare_type(result, expected_types)
#
#         assert exp_type
#         assert len(result) == 1, "Ожидается только одна запись"
#         assert result == expected_data, 'Данные не соответствуют'
#         assert result_db.scalar() is not None, "Запись не найдена в базе данных"
