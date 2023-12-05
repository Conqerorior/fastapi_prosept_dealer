from typing import List, Optional, Union

from fastapi import HTTPException
from sqlalchemy import and_, asc, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.products.models import (MarketingDealer, MarketingDealerPrice,
                                 MarketingProduct)

from .models import (DelMatchingProductDealer, MatchingProductDealer,
                     MatchPositiveProductDealer, Statistics)

ModelType = Union[MarketingProduct, MarketingDealerPrice, Statistics]


async def get_data_matching_product_dealer(
        db: AsyncSession
) -> Optional[MatchingProductDealer]:
    """Получаем все объекты из модели «MatchingProductDealer».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.

    Returns:
        - Optional[MatchingProductDealer]: Объект модели «MatchingProductDealer» или None.
    """

    result = await db.execute(select(MatchingProductDealer).
                              order_by(asc(MatchingProductDealer.order)))
    return result.scalars().all()


async def get_data_by_id(db: AsyncSession, model: ModelType, id: int) -> Optional[ModelType]:
    """Получаем один объект, из выбранной модели, по значению ID.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - model (ModelType): Модель, из которой будет получен объект.
        - id (int): ID объекта модели.

    Returns:
        - Optional[ModelType]: Объект модели или None.
    """

    result = await db.execute(select(model).filter(model.id == id))
    return result.scalars().one_or_none()


async def get_dealer_name(db: AsyncSession, id: int) -> str:
    """Получаем название дилера из модели «MarketingDealer» по значению ID.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - id (int): ID объекта в модели «MarketingDealer».

    Returns:
        - str: Поле name из модели «MarketingDealer».
    """

    dealer = await db.execute(select(MarketingDealer).filter(
        MarketingDealer.id == id))
    dealer = dealer.scalars().one_or_none()
    return dealer.name


async def get_5_prosept_products(
        db: AsyncSession,
        list_ids: List[int]
) -> List[MarketingProduct]:
    """Получаем 5 объектов модели «MarketingProduct», по списку с ID.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - list_ids (List[int]): Список ID из модели «MatchingProductDealer».

    Returns:
        - List[MarketingProduct]: Список из 5 объектов модели «MarketingProduct».
    """

    prosept_products = await db.execute(select(MarketingProduct).where(
        MarketingProduct.id.in_(list_ids)))
    prosept_products = prosept_products.scalars().all()
    return prosept_products


async def create_dealer_product(
        db: AsyncSession,
        dealer_product_id: int,
        prosept_product_id: int
) -> None:
    """Обработка POST-запроса.

    - Создаем новую запись в таблице «MatchPositiveProductDealer»
    - Удаляем запись из «MatchingProductDealer».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - dealer_product_id (int): ID карточки дилера.
        - prosept_product_id (int): ID карточки товара от Просепт.
    """

    create_object = await db.execute(select(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == dealer_product_id))
    create_object = create_object.scalars().one_or_none()

    if not create_object:
        raise HTTPException(status_code=404, detail='Объект не найден')
    elif prosept_product_id not in create_object.product_ids:
        raise HTTPException(
            status_code=404,
            detail=('Для параметра prosept_product_id передайте одно из '
                    'значений ID, которые есть в списке product_ids'))

    product_id = await get_data_by_id(db, MarketingProduct, prosept_product_id)
    positive_product_dealer = MatchPositiveProductDealer(
        dealer_product_id=create_object.dealer_product_id,
        product_id=product_id.id
    )

    # Добавляем объекты в сеанс
    db.add(positive_product_dealer)

    # Удаляем из таблицы MatchingProductDealer
    await delete_dealer_product(db, dealer_product_id)

    # Сохраняем изменения в базе данных
    await db.commit()


async def patch_dealer_product(db: AsyncSession, id: int) -> None:
    """Обработка PATCH-запроса.

    Обновляем поле order в модели «MatchingProductDealer». Что-бы перенести
    объект в конец списка.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - id (int): ID карточки дилера.
    """

    max_order = await db.execute(func.max(MatchingProductDealer.order))
    max_order = max_order.scalar()

    await db.execute(update(MatchingProductDealer).
                     where(MatchingProductDealer.dealer_product_id == id).
                     values(order=max_order+1))
    await db.commit()


async def delete_dealer_product(db: AsyncSession, id: int) -> None:
    """Удаляем объект «MatchingProductDealer», по значению поля dealer_product_id.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - id (int): ID карточки дилера.
    """

    object_to_delete = await db.execute(select(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))

    if not object_to_delete.scalars().one_or_none():
        raise HTTPException(status_code=404, detail='Объект не найден')

    await db.execute(delete(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))
    await db.commit()


async def update_statistics(db: AsyncSession, column: str) -> None:
    """Обновляем статистику в полученном поле модели «Statistics».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - column (str): Поле из модели «Statistics».
    """

    id = 1  # В теории тут можно будет передавать ID оператора
    values = await db.scalar(select(getattr(Statistics, column)).
                             where(Statistics.id == id))

    await db.execute(update(Statistics).
                     where(Statistics.id == id).
                     values({column: values + 1}))
    await db.commit()


async def save_delete_dealer_product(db: AsyncSession, id: int) -> None:
    """Обработка DELETE-запроса.

    - Сохраняем новый объект в модели «DelMatchingProductDealer».
    - Удаляем объект в модели «MatchingProductDealer», по значению поля dealer_product_id.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - id (int): ID карточки дилера.
    """

    cur_object = await db.execute(select(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))
    cur_object = cur_object.scalars().one_or_none()

    if not cur_object:
        raise HTTPException(status_code=404, detail='Объект не найден')

    new_del_matching_product_dealer = DelMatchingProductDealer(
        dealer_product_id=cur_object.dealer_product_id,
        product_ids=cur_object.product_ids
    )

    db.add(new_del_matching_product_dealer)
    await delete_dealer_product(db, id)
    await db.commit()


async def get_match_positive_product_dealer(
        db: AsyncSession,
        dealer_product_id: int,
        prosept_product_id: int
) -> Optional[MatchPositiveProductDealer]:
    """
    Получаем объект из модели «MatchPositiveProductDealer».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - dealer_product_id (int): ID карточки дилера.
        - prosept_product_id (int): ID карточки товара «Просепт».

    Returns:
        - Optional[MatchPositiveProductDealer]: Объект «MatchPositiveProductDealer» или None.
    """

    model = MatchPositiveProductDealer
    result = await db.execute(
        select(model).
        filter(
            and_(model.dealer_product_id == dealer_product_id,
                 model.product_id == prosept_product_id)
        )
    )
    return result.scalars().one_or_none()
