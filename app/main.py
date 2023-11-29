from fastapi import FastAPI

from app.admin.admin import setup_admin
from app.auth.routers import user_router
from app.db.database import engine
from app.matching.routers import matching_router
from app.products.routers import products_router

app = FastAPI(title='FastAPI Prosept Dealer')
setup_admin(app, engine)


app.include_router(user_router)
app.include_router(products_router)
app.include_router(matching_router)
