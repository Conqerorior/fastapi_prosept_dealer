"""Подготавливаем данные от DS и загружаем их в БД."""
import os
import pickle
from typing import List

import pandas as pd
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.products.models import (MarketingDealerPrice, MarketingProduct,
                                 MarketingProductDealerKey)

from .models import MatchingProductDealer
from .script_ds import matching_predict, matching_training


async def data_preparation(
        db: AsyncSession = Depends(get_db)
) -> List[MatchingProductDealer]:
    """Подготавливаем данные от DS. Функция вернёт список со словарями.

    - Получаем данные из моделей MarketingProductDealerKey, MarketingProduct,
      и MarketingDealerPrice, преобразуем их в списки со словарями.
    - Обучаем модель DS, и передаём данные в функцию для предсказания.
    - Добавляем в каждый словарь дополнительный ключ «dealerprice_id», для
      связи с объектами модели «MarketingDealerPrice».
    - В каждом словаре объединяем полученные пять ID в один список.
    - Создаём объекты модели «MatchingProductDealer».

    Args:
        db(AsyncSession): Асинхронная сессия для доступа к базе данных.

    Returns:
        List[MatchingProductDealer]: Список объектов MatchingProductDealer.
    """

    # Получаем данные из трёх моделей
    productdealerkey = await db.execute(select(MarketingProductDealerKey))
    product = await db.execute(select(MarketingProduct))
    dealerprice = await db.execute(select(MarketingDealerPrice))

    # Преобразуем данные из моделей в список со словарями
    lst_dict_pr = [item.to_dict() for item in product.scalars().all()]
    lst_dict_dr = [item.to_dict() for item in dealerprice.scalars().all()]
    lst_dict_k = [item.to_dict() for item in productdealerkey.scalars().all()]

    # Обучаем модель DS, и передаём данные в функцию для предсказания.
    def training_match(name_model, name_features):
        """
        Проверяем если есть обученная модель передаем ее,
        Если нет то обучаем и сохраняем в папку csv.

        Args:
            Передаем в виде строчки название
            файла который будет создан или искать в папке csv.

        Returns:
            Возвращается обученную модель.
        """
        try:

            Pkl_filename = os.path.join(f'app/csv/{name_model}')

            with open(Pkl_filename, 'rb') as file:
                model = pickle.load(file)

                features_mp = pd.read_csv(
                    os.path.join(f'app/csv/{name_features}'), index_col=[0])

            return model, features_mp

        except FileNotFoundError:

            model, features_mp = matching_training(
                lst_dict_pr, lst_dict_dr, lst_dict_k)

            return model, features_mp

    matching = matching_predict(
        lst_dict_pr, lst_dict_dr, training_match(
            'Pikel_model.pkl',
            'features_mp.csv'))

    """
    Добавляем в каждый словарь дополнительный ключ «dealerprice_id», что-бы
    была связь между полученными id и объектами модели «MarketingDealerPrice».
    """
    if len(matching) == len(lst_dict_dr):
        for match_dict, dr_dict in zip(matching, lst_dict_dr):
            match_dict['dealerprice_id'] = dr_dict['id']

    """
    - В каждом словаре объединяем полученные пять ID в один список.
    - И создаём объекты модели «MatchingProductDealer».
    """
    matching_products = []
    for dict_item in matching:
        product_ids = [dict_item[str(i)] for i in range(1, 6)]

        new_matching_product = MatchingProductDealer(
            product_ids=product_ids,
            dealer_product_id=dict_item['dealerprice_id'])

        matching_products.append(new_matching_product)

    return matching_products


async def load_data(session: AsyncSession) -> None:
    """Загрузка подготовленных данных матчинга в БД."""

    matching_products = await data_preparation(session)
    try:
        for item in matching_products:
            session.add(item)
            await session.flush()
            item.order = item.id
        await session.commit()
        print('Данные DS добавлены в БД.')
    except Exception as e:
        await session.rollback()
        raise e
