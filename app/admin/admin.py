from sqladmin import Admin, ModelView

from app.matching.models import MatchingProductDealer
from app.products.models import (MarketingDealer, MarketingDealerPrice,
                                 MarketingProduct)


def setup_admin(app, engine):
    admin = Admin(app, engine, title='Админ Панель')

    class MarketingDealerAdmin(ModelView, model=MarketingDealer):
        """Отображение Модели Маркетинг Дилер."""

        name = 'Дилер'
        name_plural = 'Дилеры'
        column_labels = {MarketingDealer.name: 'Имя Дилера'}
        column_list = [MarketingDealer.id, MarketingDealer.name]

    class MarketingDealerPriceAdmin(ModelView, model=MarketingDealerPrice):
        """Отображение Модели Цена Дилера."""

        name = 'Продукты Дилера'
        name_plural = 'Продукты Дилеров'
        column_labels = {
            MarketingDealerPrice.price: 'Цена',
            MarketingDealerPrice.product_name: 'Имя Продукта',
            MarketingDealerPrice.product_url: 'Ссылка на Продукт',
            MarketingDealerPrice.date: 'Дата',
        }
        column_searchable_list = [
            MarketingDealerPrice.product_name
        ]
        column_sortable_list = [
            MarketingDealerPrice.date
        ]
        column_list = [
            MarketingDealerPrice.id,
            MarketingDealerPrice.price,
            MarketingDealerPrice.product_name,
            MarketingDealerPrice.product_url,
            MarketingDealerPrice.date
        ]

    class MarketingProductAdmin(ModelView, model=MarketingProduct):
        """Отображение Модели Просепт."""

        def colum_format(self, value):
            """Функция регулирования ширины колонки."""

            return self.name[:40] if value else ''

        name = 'Просепт'
        name_plural = 'Продукты Просепта'
        column_searchable_list = [
            MarketingProduct.name
        ]
        column_sortable_list = [
            MarketingProduct.id
        ]
        column_labels = {
            MarketingProduct.name: 'Имя',
            MarketingProduct.cost: 'Цена',
            MarketingProduct.ean_13: 'Код Товара',
            MarketingProduct.article: 'Артикул',
            MarketingProduct.min_recommended_price: 'Рекомендованная мин.цена',
            MarketingProduct.recommended_price: 'Рекомендованная Цена',
        }

        column_formatters = {
            'name': colum_format
        }
        column_list = [
            MarketingProduct.id,
            MarketingProduct.name,
            MarketingProduct.cost,
            MarketingProduct.ean_13,
            MarketingProduct.article,
            MarketingProduct.category_id,
            MarketingProduct.min_recommended_price,
            MarketingProduct.recommended_price,
        ]

    class MatchingProductDealerAdmin(ModelView, model=MatchingProductDealer):
        """Отображение модели матчинга."""

        name = 'Матчинг товаров'
        name_plural = 'Матчинг товаров'
        column_labels = {
            MatchingProductDealer.product_ids: 'Пять ID товаров от Просепт',
            MatchingProductDealer.dealer_product_id: 'ID товара от диллера',
            MatchingProductDealer.order: 'Поле для сортировки.'
        }
        column_default_sort = [('order', False)]
        column_sortable_list = [
            MatchingProductDealer.order
        ]
        column_list = [
            MatchingProductDealer.id,
            MatchingProductDealer.dealer_product_id,
            MatchingProductDealer.product_ids,
            MatchingProductDealer.order
        ]

    admin.add_view(MarketingDealerAdmin)
    admin.add_view(MarketingDealerPriceAdmin)
    admin.add_view(MarketingProductAdmin)
    admin.add_view(MatchingProductDealerAdmin)
