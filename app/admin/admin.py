from sqladmin import Admin, ModelView
from app.models.models import (MarketingDealer,
                               MarketingDealerPrice,
                               MarketingProduct)


def setup_admin(app, engine):
    admin = Admin(app, engine, title='Админ Панель')

    class MarketingDealerAdmin(ModelView, model=MarketingDealer):
        """Отображение Модели Маркетинг Дилер."""

        name = 'Дилер'
        name_plural = 'Дилеры'
        column_list = [MarketingDealer.id, MarketingDealer.name]

    class MarketingDealerPriceAdmin(ModelView, model=MarketingDealerPrice):
        """Отображение Модели Цена Дилера."""

        name = 'Продукты Дилера'
        name_plural = 'Продукты Дилеров'
        column_list = [
            MarketingDealerPrice.id,
            MarketingDealerPrice.price,
            MarketingDealerPrice.product_name,
            MarketingDealerPrice.product_url,
            MarketingDealerPrice.date
        ]

    class MarketingProductAdmin(ModelView, model=MarketingProduct):
        """Отображение Модели Просепт."""

        name = 'Просепт'
        name_plural = 'Продукты Просепта'
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

    admin.add_view(MarketingDealerAdmin)
    admin.add_view(MarketingDealerPriceAdmin)
    admin.add_view(MarketingProductAdmin)
