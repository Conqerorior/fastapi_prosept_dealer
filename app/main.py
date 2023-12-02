from fastapi import FastAPI

from app.admin.admin import setup_admin
from app.db.database import engine
from app.matching.routers import api_version1

app = FastAPI(title='FastAPI Prosept Dealer')
setup_admin(app, engine)


app.include_router(api_version1)
