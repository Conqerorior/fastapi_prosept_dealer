from typing import Optional

from pydantic import BaseModel, Field, conlist

from app.products.schemas import MarketingProductModel


class DealerProductModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealer_name: str = Field(description='Название дилера')
    product_name: str = Field(description='Название товара')
    price: float = Field(description='Цена')
    product_url: Optional[str] = Field(None, description='Ссылка на товар')


class MatchingProductDealerModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealer_product: DealerProductModel = Field(
        description='Карточка товара дилера'
    )
    products: conlist(
        MarketingProductModel, min_length=5, max_length=5) = Field(
            description='Список который содержит пять товаров от Просепт'
    )
