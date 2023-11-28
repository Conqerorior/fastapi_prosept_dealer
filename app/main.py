from fastapi import FastAPI

from app.auth.routers import user_router
from app.products.routers import products_router
from app.admin.routers import admin_router

app = FastAPI(title='FastAPI Prosept Dealer')

app.include_router(user_router)
app.include_router(products_router)
app.include_router(admin_router)
