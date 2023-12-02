from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class MarketingDealer(Base):
    """Cписок дилеров."""

    __tablename__ = 'marketing_dealer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class MarketingDealerPrice(Base):
    """Результат работы парсера площадок дилеров."""

    __tablename__ = 'marketing_dealerprice'

    id = Column(Integer, primary_key=True, index=True)
    product_key = Column(
        String, comment='уникальный номер позиции', unique=True
    )
    price = Column(Float, comment='цена', nullable=False)
    product_url = Column(
        String, nullable=False,
        comment='адрес страницы, откуда собраны данные'
    )
    product_name = Column(
        String, nullable=False,
        comment='заголовок продаваемого товара'
    )
    date = Column(DateTime, comment='дата получения информации')
    dealer_id = Column(
        Integer, ForeignKey("marketing_dealer.id"),
        comment='идентификатор дилера', nullable=False
    )

    dealer = relationship("MarketingDealer")

    def to_dict(self):
        """
        Вспомогательный метод, преобразования данных в список со
        словарями. Что-бы была возможность передать необходимые данные
        в функцию для ML.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MarketingProduct(Base):
    """Список товаров, которые производит и распространяет «Просепт»."""

    __tablename__ = 'marketing_product'

    id = Column(Integer, primary_key=True, index=True)
    article = Column(Integer, comment='артикул товара', nullable=False)
    ean_13 = Column(String, comment='код товара')
    cost = Column(Float, comment='стоимость', nullable=False)
    name = Column(String, comment='название товара')
    min_recommended_price = Column(
        Float, comment='рекомендованная минимальная цена'
    )
    recommended_price = Column(Float, comment='рекомендованная цена')
    category_id = Column(String, comment='категория товара')
    ozon_name = Column(String, comment='названиет товара на Озоне')
    name_1c = Column(String, comment='название товара в 1C', nullable=False)
    wb_name = Column(String, comment='название товара на Wildberries')
    ozon_article = Column(String, comment='описание для Озон')
    wb_article = Column(String, comment='артикул для Wildberries')
    ym_article = Column(String, comment='артикул для Яндекс.Маркета')
    wb_article_td = Column(String, comment='артикул для Wildberries td')

    def to_dict(self):
        """
        Вспомогательный метод, преобразования данных в список со
        словарями. Что-бы была возможность передать необходимые данные
        в функцию для ML.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MarketingProductDealerKey(Base):
    """Таблица матчинга товаров «Просепт» и товаров дилеров."""

    __tablename__ = 'marketing_productdealerkey'

    id = Column(Integer, primary_key=True)
    key = Column(String, ForeignKey('marketing_dealerprice.product_key'))
    product_id = Column(Integer, ForeignKey('marketing_product.id'))
    dealer_id = Column(Integer, ForeignKey('marketing_dealer.id'))

    dealerprice = relationship("MarketingDealerPrice")
    product = relationship("MarketingProduct")
    dealer = relationship("MarketingDealer")

    def to_dict(self):
        """
        Вспомогательный метод, преобразования данных в список со
        словарями. Что-бы была возможность передать необходимые данные
        в функцию для ML.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
