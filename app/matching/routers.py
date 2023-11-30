from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.products.crud import get_all_data, get_data_by_id
from app.products.models import MarketingDealerPrice, MarketingProduct

from .models import MatchingProductDealer
from .schemas import MatchingProductDealerModel

matching_router = APIRouter()


@matching_router.get('/matching_product_dealer', tags=['Матчинг'],
                     response_model=List[MatchingProductDealerModel],
                     summary=('Список наиболее вероятных карточек '
                              'производителя для каждой карточки диллера'))
async def compare_products(db: AsyncSession = Depends(get_db)):
    """Выводим объекты модели «MatchingProductDealer»"""

    matching_products = await get_all_data(db, MatchingProductDealer)

    response = []
    for matching_product in matching_products:
        # Получаем объект модели MarketingDealerPrice
        dealerprice = await get_data_by_id(db, MarketingDealerPrice,
                                           matching_product.dealerprice_id)

        # Получаем сразу все 5 объектов модели MarketingProduct
        products = await db.execute(select(MarketingProduct).where(
            MarketingProduct.id.in_(matching_product.product_ids)))
        products = products.scalars().all()

        # Сортируем продукты в нужном порядке, как в списке product_ids
        products_dict = {product.id: product for product in products}
        sorted_products = [products_dict[id] for id in
                           matching_product.product_ids if id in products_dict]

        # Преобразуем данные
        lst_dict_products = [item.to_dict() for item in sorted_products]
        dict_dealerprice = dealerprice.to_dict()

        response.append(MatchingProductDealerModel(
            id=matching_product.id,
            dealerprice=dict_dealerprice,
            products=lst_dict_products
        ))

    return response
