from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from .crud import get_all_data, get_data_by_id
from .models import MarketingDealer, MarketingDealerPrice, MarketingProduct
from .schemas import (MarketingDealerModel, MarketingDealerPriceModel,
                      MarketingProductModel)

products_router = APIRouter()


@products_router.get("/dealers", summary='Список диллеров',
                     response_model=List[MarketingDealerModel],
                     tags=['Список всех объектов'])
async def read_dealers(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingDealer»"""

    items = await get_all_data(db, MarketingDealer)
    return items


@products_router.get("/products", summary='Список товаров Просепт',
                     response_model=List[MarketingProductModel],
                     tags=['Список всех объектов'])
async def read_products(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingProduct»"""

    items = await get_all_data(db, MarketingProduct)
    return items


@products_router.get("/products/{id}", tags=['Получение объекта по ID'],
                     summary='Получение товара Просепт по ID',
                     response_model=MarketingProductModel)
async def product_by_id(db: AsyncSession = Depends(get_db),
                        id: int = Path(..., description='ID товара')):
    """Выводит объект модели «MarketingProduct» по ID

    Данный запрос можно написать для всех моделей, но пока создал
    только для одной модели.
    """

    items = await get_data_by_id(db, MarketingProduct, id)
    return items


@products_router.get("/dealerprice", summary='Список товаров от парсера',
                     response_model=List[MarketingDealerPriceModel],
                     tags=['Список всех объектов'])
async def read_dealerprice(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingDealerPrice»"""

    items = await get_all_data(db, MarketingDealerPrice)
    return items
