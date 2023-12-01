from fastapi import HTTPException
from sqlalchemy import Delete, asc, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.products.models import MarketingDealer, MarketingProduct

from .models import MatchingProductDealer, MatchPositiveProductDealer


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


async def get_all_dealer_product_ids(db: AsyncSession):
    """Получаем все поля dealer_product_id модели «MatchingProductDealer».

    Получаем список ID всех карточек дилера.
    """

    result = await db.execute(select(MatchingProductDealer.dealer_product_id).
                              order_by(asc(MatchingProductDealer.order)))
    dealerprice_ids = result.scalars().all()
    return dealerprice_ids


async def create_dealer_product(db: AsyncSession, id: int):
    """Создаем новую запись в таблице MatchPositiveProductDealer
    и удаляем запись из MatchingProductDealer"""

    create_object = await db.execute(select(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))

    create_object = create_object.scalars().one_or_none()

    if not create_object:
        raise HTTPException(status_code=404, detail='Объект не найден')

    positive_product_dealer = MatchPositiveProductDealer(
        dealer_product_id=create_object.dealer_product_id,
        product_ids=create_object.product_ids
    )

    # Добавляем объекты в сеанс
    db.add(positive_product_dealer)

    # Удаляем из таблицы MatchingProductDealer
    await delete_dealer_product(db, create_object.id)

    # Сохраняем изменения в базе данных
    await db.commit()


async def patch_dealer_product(db: AsyncSession, id: int):
    """Обновляем поле order в моделе «MatchingProductDealer»."""

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

    await db.execute(Delete(MatchingProductDealer).where(
        MatchingProductDealer.dealer_product_id == id))
    await db.commit()
