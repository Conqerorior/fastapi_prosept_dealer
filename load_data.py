"""Скрипт для добавления данных в БД

- Сначала загружаются данные из csv файлов.
- После загрузки данных из csv запускается функция для
  загрузки данных, которые получены от DS.
- Создаём один объект в модели Statistics.
"""

import asyncio
import csv
import os
from datetime import datetime as dt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import engine
from app.matching.load_db import load_data
from app.matching.models import Statistics
from app.products.models import (MarketingDealer, MarketingDealerPrice,
                                 MarketingProduct, MarketingProductDealerKey)

"""
Каждый csv файл имеет свои особенности при добавлении данных,
поэтому был добавлен дополнительный словарь data_types,
с правилами для преобразования полей.
"""
csv_files = {
    'marketing_dealer.csv': {
        'model': MarketingDealer,
        'data_types': {}
    },
    'marketing_dealerprice.csv': {
        'model': MarketingDealerPrice,
        'data_types': {'price': float, 'date': dt, 'dealer_id': int}
    },
    'marketing_product.csv': {
        'model': MarketingProduct,
        'data_types': {
            'article': int,
            'cost': float,
            'min_recommended_price': float,
            'recommended_price': float}
    },
    'marketing_productdealerkey.csv': {
        'model': MarketingProductDealerKey,
        'data_types': {'product_id': int, 'dealer_id': int}
    }
}


def convert_data_types(row, data_types):
    """Функция для преобразования полей к необходимому типу данных.

    При работе с асинхронным кодом необходимо явно преобразовывать
    типы данных перед их вставкой в базу данных.
    """

    for key, data_type in data_types.items():
        value = row[key]

        if data_type == int and value.isdigit():
            row[key] = int(value)

        elif data_type == float:
            row[key] = float(value) if value else None

        elif data_type == dt and value:
            row[key] = dt.strptime(value, '%Y-%m-%d')

    return row


async def add_data_from_csv(file_configs, session):
    """Функция добавляет данные из CSV файлов в базу данных.

    Args:
        file_configs (dict): Словарь, содержащий настройки для каждого
                             типа файла CSV, включая модель для записи данных
                             и правила преобразования данных.
        session (AsyncSession): Асинхронная сессия для подключения к БД.
    """

    try:
        for csv_file, config in file_configs.items():
            model = config['model']
            data_types = config['data_types']
            file = os.path.join(f'app/csv/{csv_file}')
            with open(file, encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    row['id'] = int(row['id'])
                    row = convert_data_types(row, data_types)

                    item = model(**row)
                    session.add(item)

                    try:
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                        continue

            print(f'{csv_file} добавлен в БД')
    except Exception as e:
        await session.rollback()
        raise e


async def add_statistics(session: AsyncSession):
    """Создаём объект в модели Statistics."""

    new_object = Statistics(id=1)

    try:
        session.add(new_object)
        await session.commit()
        print('Объект в модели Statistics создан.')
    except Exception as e:
        await session.rollback()
        raise e


async def main():
    async with AsyncSession(engine) as session:
        await add_data_from_csv(csv_files, session)
        await add_statistics(session)
        await load_data(session)

asyncio.run(main())
