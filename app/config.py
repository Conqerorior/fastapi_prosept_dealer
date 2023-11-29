"""Переменные окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
SECRET_KEY = os.environ.get("SECRET_KEY")
