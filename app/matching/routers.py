from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.products.models import MarketingDealerPrice

from .crud import (delete_dealer_product, get_5_prosept_products, get_all_data,
                   get_all_dealer_product_ids, get_data_by_id, get_dealer_name,
                   patch_dealer_product)
from .models import MatchingProductDealer
from .schemas import DealerProductModel, MatchingProductDealerModel

matching_router = APIRouter()
products_router = APIRouter()


@products_router.get("/dealer_products", tags=['Карточки дилера'],
                     response_model=List[DealerProductModel],
                     summary='Список всех карточек от дилера')
async def read_dealer_products(db: AsyncSession = Depends(get_db)):
    """
    - Получаем все объекты модели «MarketingDealerPrice», по значениям
      ID, из поля dealer_product_id модели «MatchingProductDealer».

    - Получаем все карточки с товарами дилеров.
    """

    response = []

    dealerprice_ids = await get_all_dealer_product_ids(db)
    for id in dealerprice_ids:
        obj = await get_data_by_id(db, MarketingDealerPrice, id)

        response.append(DealerProductModel(
            id=obj.id,
            dealer_name=await get_dealer_name(db, obj.dealer_id),
            product_name=obj.product_name,
            price=obj.price,
            product_url=obj.product_url
        ))

    return response


@products_router.get("/dealer_products/{id}", tags=['Карточки дилера'],
                     response_model=DealerProductModel,
                     summary='Карточка дилера по ID')
async def dealer_products_by_id(db: AsyncSession = Depends(get_db),
                                id: int = Path(..., description='ID объекта')):
    """
    - Получаем объект модели «MarketingDealerPrice» по значению ID,
      из поля поля dealer_product_id модели «MatchingProductDealer».

    - Получаем карточку дилера по ID.
    """

    obj = await get_data_by_id(db, MarketingDealerPrice, id)

    response = DealerProductModel(
        id=obj.id,
        dealer_name=await get_dealer_name(db, obj.dealer_id),
        product_name=obj.product_name,
        price=obj.price,
        product_url=obj.product_url
    )

    return response


@matching_router.get('/matching', tags=['Матчинг'],
                     response_model=List[MatchingProductDealerModel],
                     summary=('Список наиболее вероятных карточек '
                              'производителя для каждой карточки дилера'))
async def read_dealer_product(db: AsyncSession = Depends(get_db)):
    """
    - Получаем все объекты модели «MatchingProductDealer».
    - В каждом объекте одна карточка дилера и пять карточек товаров Просепт.
    """

    response = []

    matching_products = await get_all_data(db, MatchingProductDealer)
    for matching_product in matching_products:

        """
        Получаем один объект дилера, и получаем для него все
        необходимые значения, которые нужно передать фронтам
        """
        dealer_product = await get_data_by_id(
            db, MarketingDealerPrice,
            matching_product.dealer_product_id)

        dealer_pydantic = DealerProductModel(
            id=dealer_product.id,
            product_name=dealer_product.product_name,
            price=dealer_product.price,
            product_url=dealer_product.product_url,
            dealer_name=await get_dealer_name(db, dealer_product.dealer_id))

        """
        - Получаем сразу все 5 карточек товаров Просепт по значениям ID
          из списка product_ids.
        - Сортируем их в первоночальном варианте.
        """
        prosept_products = await get_5_prosept_products(
            db, matching_product.product_ids)

        products_dict = {product.id: product for product in prosept_products}
        sorted_products = [products_dict[id] for id in
                           matching_product.product_ids if id in products_dict]

        # Сохраняем результат
        lst_dict_products = [item.to_dict() for item in sorted_products]
        response.append(MatchingProductDealerModel(
            id=matching_product.id,
            dealer_product=dealer_pydantic,
            products=lst_dict_products
        ))

    return response


@matching_router.delete('/matching/{dealer_product_id}',
                        tags=['Матчинг'], response_model=None,
                        summary='Удалить карточку дилера')
async def delete_product(
    dealer_product_id: int = Path(..., description='ID карточки дилера'),
    db: AsyncSession = Depends(get_db)
):
    """
    - Удаляем объект модели «MatchingProductDealer», по значению
      поля dealer_product_id.

    - Удаляем карточку дилера и 5 связанных с ним карточек товаров Просепт.
    """

    await delete_dealer_product(db, dealer_product_id)


@matching_router.patch('/matching/{dealer_product_id}',
                       tags=['Матчинг'], response_model=None,
                       summary='Перенести карточку дилера в конец списка')
async def patch_product(
    dealer_product_id: int = Path(..., description='ID карточки дилера'),
    db: AsyncSession = Depends(get_db)
):
    """
    - Меняем поле order в модели «MatchingProductDealer», что-бы при сортировке
      по этому полю изменённый объект оказался в конце списка.

    - Переносим выбранную карточку дилера в конец списка.
    """

    await patch_dealer_product(db, dealer_product_id)
