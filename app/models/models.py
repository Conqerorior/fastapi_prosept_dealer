from datetime import datetime

from sqlalchemy import (
    MetaData,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Table,
    Column)

metadata = MetaData()

marketing_dealer = Table(
    'marketing_dealer',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
)

marketing_dealerprice = Table(
    'marketing_dealer',
    metadata,
    Column('product_key', Integer, primary_key=True),
    Column('price', Integer, nullable=False),
    Column('product_url', String, nullable=False),
    Column('product_name', String, nullable=False),
    Column('date', TIMESTAMP, default=datetime.utcnow),
    Column('dealer_id', Integer, ForeignKey('marketing_dealer.id')),
)

marketing_product = Table(
    'marketing_product',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('article', String, nullable=False),
    Column('ean_13', String, nullable=False),
    Column('name', String, nullable=False),
    Column('cost', String, nullable=False),
    Column('min_recommended_price', String, nullable=False),
    Column('recommended_price', String, nullable=False),
    Column('category_id', String, nullable=False),
    Column('ozon_name', String, nullable=False),
    Column('name_1c', String, nullable=False),
    Column('wb_name', String, nullable=False),
    Column('ozon_article', String, nullable=False),
    Column('wb_article', String, nullable=False),
    Column('ym_article', String, nullable=False)
)

marketing_productdealerkey = Table(
    'marketing_productdealerkey',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('key', Integer, ForeignKey('marketing_dealerprice.id')),
    Column('product_id', Integer, ForeignKey('marketing_product.id')),
    Column('dealer_id', Integer, ForeignKey('marketing_dealer.id'))
)
