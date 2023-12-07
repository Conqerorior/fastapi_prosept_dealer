"""Переменные окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS").split(',')

DB_TEST_USER = os.environ.get('DB_TEST_USER')
DB_TEST_PASSWORD = os.environ.get('DB_TEST_PASSWORD')
DB_TEST_HOST = os.environ.get('DB_TEST_HOST')
DB_TEST_PORT = os.environ.get('DB_TEST_PORT')
DB_TEST_NAME = os.environ.get('DB_TEST_NAME')
