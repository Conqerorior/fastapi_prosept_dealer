from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MarketingDealerModel(BaseModel):
    id: int
    name: str


class MarketingProductModel(BaseModel):
    id: int
    article: int
    ean_13: str
    cost: Optional[float] = None
    name: Optional[str] = None
    min_recommended_price: Optional[float] = None
    recommended_price: Optional[float] = None
    category_id: Optional[str] = None
    ozon_name: Optional[str] = None
    name_1c: Optional[str] = None
    wb_name: Optional[str] = None
    ozon_article: Optional[str] = None
    wb_article: Optional[str] = None
    ym_article: Optional[str] = None
    wb_article_td: Optional[str] = None


class MarketingDealerPriceModel(BaseModel):
    id: int
    product_key: str
    price: float
    product_url: Optional[str] = None
    product_name: str
    date: datetime
    dealer_id: int
