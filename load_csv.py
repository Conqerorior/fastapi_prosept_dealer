"""Скрипт для добавления данных из csv файлов в БД."""

import csv
import os

from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.models.models import (MarketingDealer, MarketingDealerPrice,
                               MarketingProduct, MarketingProductDealerKey)

csv_files_and_models = {
    'marketing_dealer.csv': MarketingDealer,
    'marketing_dealerprice.csv': MarketingDealerPrice,
    'marketing_product.csv': MarketingProduct,
    'marketing_productdealerkey.csv': MarketingProductDealerKey
}


def add_data_from_csv(models):
    db = SessionLocal()
    try:
        for csv_file, model in models.items():
            file = os.path.join(f'app/csv/{csv_file}')
            with open(file, encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:

                    if csv_file == 'marketing_product.csv':
                        row = {
                            key: (value if value.strip() != '' else None)
                            for key, value in row.items()}

                    try:
                        item = model(**row)
                        db.add(item)
                        db.commit()
                    except IntegrityError:
                        db.rollback()
            print(f'{csv_file} добавлен в БД')
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


add_data_from_csv(csv_files_and_models)
