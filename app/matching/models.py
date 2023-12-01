from sqlalchemy import ARRAY, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class MatchingProductDealer(Base):
    """Матчинг товаров Просепт и товаров дилеров от наших DS."""

    __tablename__ = 'matching_product_dealer'

    id = Column(Integer, primary_key=True, index=True)
    product_ids = Column(ARRAY(Integer), comment='Пять ID товаров от Просепт')
    dealer_product_id = Column(
        Integer, ForeignKey('marketing_dealerprice.id'),
        comment='ID товара от диллера'
    )
    order = Column(
        Integer,
        comment='Поле для сортировки. Для реализации кнопки «Отложить»')

    dealerprice = relationship("MarketingDealerPrice")
