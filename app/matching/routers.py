from typing import List

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.products.models import MarketingDealerPrice, MarketingProduct

from .crud import (create_dealer_product, get_5_prosept_products,
                   get_data_by_id, get_data_matching_product_dealer,
                   get_dealer_name, get_match_positive_product_dealer,
                   patch_dealer_product, save_delete_dealer_product,
                   update_statistics)
from .models import Statistics
from .schemas import (DealerProductModel, MatchingProductDealerModel,
                      MatchPositiveProductDealerModel, ProductData,
                      StatisticsData)

api_version1 = APIRouter()


@api_version1.get('/api/v1/matching', tags=['Матчинг'],
                  response_model=List[MatchingProductDealerModel],
                  summary=('Список наиболее вероятных карточек '
                           'производителя для каждой карточки дилера'))
async def read_dealer_product(db: AsyncSession = Depends(get_db)):
    """
    - Получаем все объекты модели «MatchingProductDealer».
    - В каждом объекте одна карточка дилера и пять карточек товаров Просепт.
    """

    response = []

    matching_products = await get_data_matching_product_dealer(db)
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


@api_version1.post('/api/v1/matching/{dealer_product_id}', tags=['Матчинг'],
                   response_model=MatchPositiveProductDealerModel,
                   status_code=status.HTTP_201_CREATED,
                   summary='Сохранение карточки после обработки оператором')
async def post_product(
        prosept_product_id: ProductData,
        dealer_product_id: int = Path(..., description='ID карточки дилера'),
        db: AsyncSession = Depends(get_db)
):
    """
    - Удаляем объект из модели «MatchingProductDealer», по значению
      поля dealer_product_id.
    - Создаем новую запись в «MatchPositiveProductDealer» с карточкой Просепт,
      полученной по значению prosept_id.
    """

    prosept_id = prosept_product_id.prosept_id

    await create_dealer_product(db, dealer_product_id, prosept_id)
    await update_statistics(db, 'accepted_cards')

    created_object = await get_match_positive_product_dealer(
        db, dealer_product_id, prosept_id)

    dealer_product = await get_data_by_id(
        db, MarketingDealerPrice, created_object.dealer_product_id)

    dealer_pydantic = DealerProductModel(
        id=dealer_product.id,
        product_name=dealer_product.product_name,
        price=dealer_product.price,
        product_url=dealer_product.product_url,
        dealer_name=await get_dealer_name(db, dealer_product.dealer_id))

    prosept = await get_data_by_id(db, MarketingProduct, created_object.product_id)
    response = MatchPositiveProductDealerModel(
        id=created_object.id,
        dealer_product=dealer_pydantic,
        prosept_product=prosept.to_dict()
    )
    return response


@api_version1.patch('/api/v1/matching/{dealer_product_id}',
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
    await update_statistics(db, 'postponed_cards')


@api_version1.delete('/api/v1/matching/{dealer_product_id}',
                     tags=['Матчинг'], response_model=None,
                     status_code=status.HTTP_204_NO_CONTENT,
                     summary='Удалить карточку дилера')
async def delete_product(
    dealer_product_id: int = Path(..., description='ID карточки дилера'),
    db: AsyncSession = Depends(get_db)
):
    """
    - Удаляем объект модели «MatchingProductDealer», по значению
      поля dealer_product_id. И создаем новую запись в
      «DelMatchingProductDealer».
    - Удаляем карточку дилера и 5 связанных с ним карточек товаров Просепт.
    """

    await save_delete_dealer_product(db, dealer_product_id)
    await update_statistics(db, 'delete_cards')


@api_version1.get('/api/v1/statistics', tags=['Статистика'],
                  response_model=StatisticsData,
                  summary='Статистика работы оператора')
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Собираем статистику по работе оператора."""

    id = 1  # В теории тут можно будет передавать ID оператора
    obj = await get_data_by_id(db, Statistics, id)

    # Общее количество проверенных карточек
    total_cards_checked = (obj.accepted_cards + obj.delete_cards +
                           obj.postponed_cards)

    # Процент принятых карточек
    if total_cards_checked == 0:
        percentage_accepted_cards = 0
    else:
        percentage_accepted_cards = (obj.accepted_cards/total_cards_checked) * 100

    response = StatisticsData(
        total_cards_checked=total_cards_checked,
        accepted_cards=obj.accepted_cards,
        delete_cards=obj.delete_cards,
        postponed_cards=obj.postponed_cards,
        percentage_accepted_cards=round(percentage_accepted_cards, 2)
    )
    return response
