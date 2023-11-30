from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.products.models import MarketingProduct

from .models import MatchingProductDealer
from .schemas import MatchingProductDealerModel


async def get_matching_products(db: AsyncSession):
    """
    Получаем список объектов модели MatchingProductDealer с
    дополнительной информацией о товарах Просепт.

    - Извлекаем все объекты MatchingProductDealer.
    - Для каждого из них получаем связанные продукты MarketingProduct,
      сохраняя порядок их ID в product_ids.
    - Преобразуем полученные продукты в список словарей.
    - Формируем итоговый response.
    """

    matching_products = await db.execute(select(MatchingProductDealer))
    matching_products = matching_products.scalars().all()

    response = []
    for matching_product in matching_products:

        # Получаем сразу все 5 объектов модели MarketingProduct
        products = await db.execute(select(MarketingProduct).where(
            MarketingProduct.id.in_(matching_product.product_ids)))
        products = products.scalars().all()

        # Сортируем продукты в нужном порядке, как в списке product_ids
        products_dict = {product.id: product for product in products}
        sorted_products = [products_dict[id] for id in
                           matching_product.product_ids if id in products_dict]

        # Преобразуем данные в список со словарями
        lst_dict_products = [item.to_dict() for item in sorted_products]

        response.append(MatchingProductDealerModel(
            id=matching_product.id,
            dealerprice_id=matching_product.dealerprice_id,
            products=lst_dict_products
        ))

    return response
