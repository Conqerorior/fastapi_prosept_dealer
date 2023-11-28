from sqladmin import Admin, ModelView
from app.models.models import (MarketingDealer,
                               MarketingDealerPrice,
                               MarketingProduct)


def setup_admin(app, engine):
    admin = Admin(app, engine)

    class MarketingDealerAdmin(ModelView, model=MarketingDealer):
        """Отображение Модели Маркетинг Дилер."""

        column_list = [MarketingDealer.id, MarketingDealer.name]

    class MarketingDealerPriceAdmin(ModelView, model=MarketingDealerPrice):
        column_list = [
            MarketingDealerPrice.id,
            MarketingDealerPrice.price,
            MarketingDealerPrice.dealer,
            MarketingDealerPrice.product_name,
            MarketingDealerPrice.product_url,
        ]

    class MarketingProductAdmin(ModelView, model=MarketingProduct):
        """Отображение Модели Маркетинг Продукт."""

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
