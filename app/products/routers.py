from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import (MarketingDealer, MarketingDealerPrice,
                               MarketingProduct)

from .crud import get_all_data
from .matching import matching
from .schemas import (MarketingDealerModel, MarketingDealerPriceModel,
                      MarketingProductModel)

products_router = APIRouter()


@products_router.get("/dealers", summary='Список диллеров',
                     response_model=List[MarketingDealerModel])
async def read_dealers(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingDealer»"""

    items = await get_all_data(db, MarketingDealer)
    return items


@products_router.get("/products", summary='Список товаров Просепт',
                     response_model=List[MarketingProductModel])
async def read_products(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingProduct»"""

    items = await get_all_data(db, MarketingProduct)
    return items


@products_router.get("/dealerprice", summary='Список товаров от парсера',
                     response_model=List[MarketingDealerPriceModel])
async def read_dealerprice(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingDealerPrice»"""

    items = await get_all_data(db, MarketingDealerPrice)
    return items


@products_router.get('/compare', summary='Сравнение товаров')
async def compare_products(db: AsyncSession = Depends(get_db)):
    """Преобразует объекты «MarketingDealerPrice» и «MarketingProduct»
    в список словарей для передачи в функцию сравнения (matching)."""

    pr_data = await read_products(db)
    dr_data = await read_dealerprice(db)

    pr_dicts = [jsonable_encoder(item) for item in pr_data]
    dr_dicts = [jsonable_encoder(item) for item in dr_data]

    match = matching(pr_dicts, dr_dicts)

    for item in match:
        for key, value in item.items():
            for data in pr_dicts:
                if value == data['id']:
                    item[key] = data
    return match

