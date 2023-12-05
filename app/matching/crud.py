from fastapi import HTTPException
from sqlalchemy import and_, asc, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.products.models import MarketingDealer, MarketingProduct

from .models import (DelMatchingProductDealer, MatchingProductDealer,
                     MatchPositiveProductDealer, Statistics)


async def get_product_dealer(db: AsyncSession, model):
    """Получаем все объекты из выбранной модели."""

    result = await db.execute(select(model))
    return result.scalars().all()


async def get_all_data(db: AsyncSession, model):
    """Получаем все объекты из выбранной модели."""

    result = await db.execute(select(model).order_by(asc(model.order)))
    return result.scalars().all()


async def get_data_by_id(db: AsyncSession, model, id: int):
    """Получаем один объект, из выбранной модели, по значению ID."""

    result = await db.execute(select(model).filter(model.id == id))
    return result.scalars().one_or_none()


async def get_dealer_name(db: AsyncSession, id: int):
    """Получаем название дилера из модели «MarketingDealer» по значению ID."""

    dealer = await db.execute(select(MarketingDealer).filter(
        MarketingDealer.id == id))
    dealer = dealer.scalars().one_or_none()
    return dealer.name


async def get_5_prosept_products(db: AsyncSession, list_ids):
    """Получаем 5 объектов модели «MarketingProduct», по списку с ID.

    Получаем 5 карточек товаров Просепт.
    """

    prosept_products = await db.execute(select(MarketingProduct).where(
        MarketingProduct.id.in_(list_ids)))
    prosept_products = prosept_products.scalars().all()
    return prosept_products


async def create_dealer_product(db: AsyncSession, dealer_product_id: int,
                                prosept_product_id: int):
    """
    Создаем новую запись в таблице «MatchPositiveProductDealer»
    и удаляем запись из «MatchingProductDealer».

    Args:
        db (AsyncSession): Асинхронная сессия для подключения к БД.
        dealer_product_id (int): ID карточки дилера.
        prosept_product_id (int): ID карточки товара от Просепт.
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


async def patch_dealer_product(db: AsyncSession, id: int):
    """Обновляем поле order в модели «MatchingProductDealer»."""

    max_order = await db.execute(func.max(MatchingProductDealer.order))
    max_order = max_order.scalar()

    await db.execute(update(MatchingProductDealer).
                     where(MatchingProductDealer.dealer_product_id == id).
                     values(order=max_order+1))
    await db.commit()


async def delete_dealer_product(db: AsyncSession, id: int):
    """
    Удаляем объект «MatchingProductDealer», по значению поля dealer_product_id.
    """

    object_to_delete = await db.execute(select(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))

    if not object_to_delete.scalars().one_or_none():
        raise HTTPException(status_code=404, detail='Объект не найден')

    await db.execute(delete(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))
    await db.commit()


async def update_statistics(db: AsyncSession, column: str):
    """Обновляем статистику в полученном поле в модели «Statistics»."""

    id = 1  # В теории тут можно будет передавать ID оператора
    values = await db.scalar(select(getattr(Statistics, column)).
                             where(Statistics.id == id))

    await db.execute(update(Statistics).
                     where(Statistics.id == id).
                     values({column: values + 1}))
    await db.commit()


async def save_delete_dealer_product(db: AsyncSession, id: int):
    """
    - Сохраняем новый объект в модели «DelMatchingProductDealer».

    - Удаляем объект в модели «MatchingProductDealer»,
      по значению поля dealer_product_id.
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
        db: AsyncSession, dealer_product_id: int,
        prosept_product_id: int
):
    """Получаем объект из модели «MatchPositiveProductDealer»."""

    model = MatchPositiveProductDealer
    result = await db.execute(
        select(model).
        filter(
            and_(model.dealer_product_id == dealer_product_id,
                 model.product_id == prosept_product_id)
        )
    )
    return result.scalars().one_or_none()
