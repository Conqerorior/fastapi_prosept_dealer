<div id="header" align="center">
  <h1>FastAPI ProseptDealer</h1>
  <img src="https://img.shields.io/badge/Python-добавить_версию-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
</div>


# Документация API
[fastapi_proseptdealer/api/docs](https://clownvkkaschenko.github.io/ReferralSystem/)

# Запуск проекта:
- Клонируйте репозиторий и перейдите в него.
- Установите и активируйте виртуальное окружение.
- Установите зависимости из файла requirements.txt
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ``` 
- Необходимо создать файл **.env**, в корневой папке проекта, с переменными окружения, для подключения к PostgreSQL
  ```
  DB_NAME=postgres
  POSTGRES_USER=postgres
  DB_HOST=localhost
  DB_PORT=5432
  POSTGRES_PASSWORD=admin1202
  SECRET_KEY=your_secret_key_JWT
  ```
- Находясь в корневой папке проекта выполните миграции. Что-бы в БД создались таблицы.
  ```
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```
- Что-бы загрузить данные из csv файлов в БД, запустите скрипт **load_csv.py** из корневой папки проекта.
  ```
  python load_csv.py
  ```
- Для запуска сервера используйте данную команду:
  ```
  uvicorn app.main:app --reload
  ```
- После запуска сервера, документация API будет доступна по адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)