from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import (MarketingDealer, MarketingDealerPrice,
                               MarketingProduct)

from .crud import get_all_data
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
