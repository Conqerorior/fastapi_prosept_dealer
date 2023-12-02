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

    dealer_product = relationship("MarketingDealerPrice")


class MatchPositiveProductDealer(Base):
    """
    Итоговая таблица с карточкой дилера и карточкой Просепт,
    которую выбрал оператор.
    """

    __tablename__ = 'match_positive_prod_dealer'

    id = Column(Integer, primary_key=True, index=True)
    dealer_product_id = Column(
        Integer, ForeignKey('marketing_dealerprice.id'),
        comment='ID товара от дилера'
    )
    product_id = Column(
        Integer, ForeignKey('marketing_product.id'),
        comment='ID товара Просепт'
    )

    dealer_product = relationship("MarketingDealerPrice")
    product = relationship("MarketingProduct")


class DelMatchingProductDealer(Base):
    """
    Объекты у которых предложенные варианты товаров Просепт
    не соответствуют карточке дилера.
    """

    __tablename__ = 'del_matching_product_dealer'

    id = Column(Integer, primary_key=True, index=True)
    product_ids = Column(ARRAY(Integer), comment='Пять ID товаров от Просепт')
    dealer_product_id = Column(
        Integer, ForeignKey('marketing_dealerprice.id'),
        comment='ID товара от диллера'
    )

    dealer_product = relationship("MarketingDealerPrice")


class Statistics(Base):
    """Сохраняем в БД все действия оператора."""

    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True, index=True)
    accepted_cards = Column(
        Integer, default=0,
        comment='Количество принятых карточек'
    )
    delete_cards = Column(
        Integer, default=0,
        comment='Количество неподходящих карточек'
    )
    postponed_cards = Column(
        Integer, default=0,
        comment='Количество отложенных карточек'
    )
