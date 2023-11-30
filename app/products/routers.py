from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from .crud import get_all_data, get_data_by_id
from .models import MarketingDealerPrice
from .schemas import MarketingDealerPriceModel

products_router = APIRouter()


@products_router.get("/dealerprice", tags=['Карточки дилера'],
                     response_model=List[MarketingDealerPriceModel],
                     summary='Список всех карточек от дилера')
async def read_dealerprice(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MarketingDealerPrice»"""

    items = await get_all_data(db, MarketingDealerPrice)
    return items


@products_router.get("/dealerprice/{id}", tags=['Карточки дилера'],
                     summary='Получение карточки дилера по ID',
                     response_model=MarketingDealerPriceModel)
async def product_by_id(db: AsyncSession = Depends(get_db),
                        id: int = Path(..., description='ID товара')):
    """Выводит карточку товара от дилера по ID"""

    items = await get_data_by_id(db, MarketingDealerPrice, id)
    return items
