from datetime import datetime
from urllib.parse import urlparse

from httpx import AsyncClient
from sqlalchemy import insert, select
from tests.conftest import async_session_marker
from app.products.models import MarketingDealer, MarketingDealerPrice


async def data_to_dict(obj):
    """Преобразование в список словарей."""
    result = [
        {c.name: getattr(md, c.name) for c in md.__table__.columns} for md
        in obj]
    return result


async def test_marketing_dealer(async_client: AsyncClient):
    # Создаем тестовую запись в базе данных
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


async def test_marketing_dealer_price(async_client: AsyncClient):
    # Создаем тестовую запись в базе данных
    async with async_session_marker() as session:
        test_data = insert(MarketingDealerPrice).values(
            id=1,
            product_key='546227',
            price=233.00,
            product_url='https://akson.ru//p/sredstvo_universalnoe_prosept_universal_spray_500ml',
            product_name='Средство универсальное Prosept Universal Spray, 500мл',
            date=datetime(2023, 7, 11),
            dealer_id=1)

        await session.execute(test_data)
        await session.commit()

        query = select(MarketingDealerPrice)
        res = await session.execute(query)
        marketing_dealer_price = res.scalars().all()
        result = await data_to_dict(marketing_dealer_price)

        expected_data = [{
            'id': 1,
            'product_key': '546227',
            'price': 233.0,
            'product_url': 'https://akson.ru//p/sredstvo_universalnoe_prosept_universal_spray_500ml',
            'product_name': 'Средство универсальное Prosept Universal Spray, 500мл',
            'date': datetime(2023, 7, 11),
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

        for key, expected_type in expected_types.items():
            assert isinstance(result[0][key],
                              expected_type), f"Неверный тип данных для {key}"

        assert len(result) == 1, "Ожидается только одна запись"
        assert result == expected_data, 'Данные не соответствуют'
        assert result_db.scalar() is not None, "Запись не найдена в базе данных"
        assert parsed_url.scheme and parsed_url.netloc, "Неверный формат URL"
        assert result[0]['product_key'] is not None, "product_key None"
        assert result[0]['price'] > 0, "Цена должна быть положительной"
