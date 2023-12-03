from pydantic import BaseModel, Field, conlist


class DealerProductModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealer_name: str = Field(description='Название дилера')
    product_name: str = Field(description='Название товара')
    price: float = Field(description='Цена')
    product_url: str = Field(description='Ссылка на товар')


class ProseptProductModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    article: int = Field(description='Артикул товара')
    cost: float = Field(description='Цена')
    name_1c: str = Field(description='Название товара')


class MatchingProductDealerModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealer_product: DealerProductModel = Field(
        description='Карточка товара дилера'
    )
    products: conlist(
        ProseptProductModel, min_length=5, max_length=5) = Field(
            description='Список который содержит пять товаров от Просепт'
    )


class ProductData(BaseModel):
    prosept_id: int = Field(
        description='ID карточки товара от Просепт.')


class StatisticsData(BaseModel):
    total_cards_checked: int = Field(
        description='Общее количество проверенных карточек'
    )
    accepted_cards: int = Field(description='Количество принятых карточек')
    delete_cards: int = Field(description='Количество неподходящих карточек')
    postponed_cards: int = Field(description='Количество отложенных карточек')
    percentage_accepted_cards: float = Field(
        description='Процент принятых карточек')


class MatchPositiveProductDealerModel(BaseModel):
    id: int = Field(description='ID объекта в БД')
    dealer_product: DealerProductModel = Field(description='Карточка товара дилера')
    prosept_product: ProseptProductModel = Field(description='Карточка товара Просепт')
