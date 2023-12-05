<div id="header" align="center">
  <h1>Matching «Prosept» dealer</h1>
  <img src="https://img.shields.io/badge/Python-3.10.11-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/FastAPI-0.104.1-F8F8FF?style=for-the-badge&logo=FastAPI&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/PostgreSQL-555555?style=for-the-badge&logo=postgresql&logoColor=F5F5DC">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.23-F8F8FF?style=for-the-badge&logo=SQLAlchemy&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/Docker-555555?style=for-the-badge&logo=docker&logoColor=2496ED">
</div>


# Документация API
[Matching «Prosept» dealer - API redoc](https://clownvkkaschenko.github.io/ReferralSystem/)

<details><summary><h1>Запуск проекта без докера</h1></summary>

- Клонируйте репозиторий и перейдите в него.
- Установите и активируйте виртуальное окружение.
- Установите зависимости из файла requirements.txt
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ``` 
- Создайте файл **.env**, в корневой папке проекта, с переменными окружения.
  ```
  DB_NAME=postgres
  POSTGRES_USER=postgres
  DB_HOST=localhost
  DB_PORT=5432
  POSTGRES_PASSWORD=password
  CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
  ```
- Находясь в корневой папке проекта выполните миграции.
  ```
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```
- Загрузите в базу данных подготовленные данные.

  P.S. Выполнение скрипта может занять продолжительное время(~10 минут)
  ```
  python load_data.py
  ```
- Для запуска сервера используйте данную команду:
  ```
  uvicorn app.main:app --reload
  ```
- Документация к API будет доступна по url-адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

- Админка, с некоторыми таблицами БД, будет доступна по url-адресу [127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

</details>

<details><summary><h1>Запуск проекта через докер</h1></summary>

- Клонируйте репозиторий.
- Перейдите в папку **infra** и создайте в ней файл **.env** с переменными окружения:
    ```
  DB_NAME=postgres
  POSTGRES_USER=postgres
  DB_HOST=db
  DB_PORT=5432
  POSTGRES_PASSWORD=password
  CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
  PGADMIN_DEFAULT_EMAIL=user@gmail.ru
  PGADMIN_DEFAULT_PASSWORD=user_password
    ``` 
- Из папки **infra** запустите docker-compose:
  ```
  ~$ docker-compose up -d --build
  ```
- В контейнере **backend** выполните миграции:
  ```
  ~$ docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

  ~$ docker-compose exec backend alembic upgrade head
  ```
- Загрузите в базу данных подготовленные данные.

  P.S. Выполнение скрипта может занять продолжительное время(~10 минут)
  ```
  ~$ docker-compose exec backend python load_data.py
  ```

Документация к API будет доступна по url-адресу [127.0.0.1/redoc](http://127.0.0.1/redoc)

Админка, с некоторыми таблицами БД, будет доступна по url-адресу [127.0.0.1/admin](http://127.0.0.1/admin)

WEB-PgAdmin будет доступен по url-адресу [127.0.0.1:5050](http://127.0.0.1:5050/)

</details>

# Авторы:

* **Backend:**
  + [Сергей](https://github.com/Conqerorior)
  + [Иван](https://github.com/clownvkkaschenko)

* **Data Science:**
  + Кристина
  + Юлия
  + Александр

* **Frontend:**
  + Дмитрий
  + Глеб
