from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.admin import setup_admin
from app.config import CORS_ORIGINS
from app.db.database import engine
from app.matching.routers import api_version1

app = FastAPI(title='FastAPI Prosept Dealer')

origins = CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

setup_admin(app, engine)


app.include_router(api_version1)
