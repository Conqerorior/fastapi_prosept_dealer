from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.products.models import (MarketingDealerPrice, MarketingProduct,
                                 MarketingProductDealerKey)

from .script_ds import match

matching_router = APIRouter()


@matching_router.get('/compare')
async def compare_products(db: AsyncSession = Depends(get_db)):

    # Получаем данные из трёх моделей
    productdealerkey = await db.execute(select(MarketingProductDealerKey))
    product = await db.execute(select(MarketingProduct))
    dealerprice = await db.execute(select(MarketingDealerPrice))

    # Преобразуем данные из моделей в список со словарями
    lst_dict_pr = [item.to_dict() for item in product.scalars().all()]
    lst_dict_dr = [item.to_dict() for item in dealerprice.scalars().all()]
    lst_dict_k = [item.to_dict() for item in productdealerkey.scalars().all()]

    # Функция от DS. Создаёт список со словарями, которые хранят 5 id
    matching = match(lst_dict_pr, lst_dict_dr, lst_dict_k)

    """
    Добавляем в каждый словарь новый ключ «dealerprice_id», что-бы
    была связь между полученными id и объектами модели MarketingDealerPrice,
    к которым относятся полученные id.
    """
    if len(matching) == len(lst_dict_dr):
        for match_dict, dr_dict in zip(matching, lst_dict_dr):
            match_dict['dealerprice_id'] = dr_dict['id']

    """
    В результате получаем список с такими словарями:
    [{"1":12,"2":159,"3":429,"4":464,"5":489,"dealerprice_id":2}]
    """
    return matching
