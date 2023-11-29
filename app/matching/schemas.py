from pydantic import BaseModel, Field, conlist


class MatchingProductDealerModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealerprice_id: int = Field(description='ID товара от дилера')
    product_ids: conlist(int, min_length=5, max_length=5) = Field(
        description='Список который содержит пять ID товаров от Просепт')
