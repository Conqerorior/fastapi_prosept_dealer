from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from .crud import get_all_data
from .models import MatchingProductDealer
from .schemas import MatchingProductDealerModel

matching_router = APIRouter()


@matching_router.get('/matching/product_dealer', tags=['Матчинг'],
                     response_model=List[MatchingProductDealerModel],
                     summary=('Список наиболее вероятных карточек '
                              'производителя для каждой карточки диллера'))
async def compare_products(db: AsyncSession = Depends(get_db)):
    """Выводит объекты модели «MatchingProductDealer»"""

    items = await get_all_data(db, MatchingProductDealer)
    return items
