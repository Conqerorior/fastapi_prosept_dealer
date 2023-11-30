from pydantic import BaseModel, Field, conlist

from app.products.schemas import MarketingProductModel


class MatchingProductDealerModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealerprice_id: int = Field(description='ID товара от дилера')
    products: conlist(
        MarketingProductModel, min_length=5, max_length=5) = Field(
            description='Список который содержит пять товаров от Просепт'
    )
