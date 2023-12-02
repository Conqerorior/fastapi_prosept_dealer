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
- Необходимо создать файл **.env**, в корневой папке проекта, с переменными окружения.
  ```
  DB_NAME=postgres
  POSTGRES_USER=postgres
  DB_HOST=localhost
  DB_PORT=5432
  POSTGRES_PASSWORD=postgres
  ```
- Находясь в корневой папке проекта выполните миграции.
  ```
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```
- Что-бы загрузить данные из csv файлов в БД, и данные полученные от DS, запустите скрипт **load_data.py** из корневой папки проекта.

  P.S. Выполнение скрипта может занять продолжительное время.
  ```
  python load_data.py
  ```
- Для запуска сервера используйте данную команду:
  ```
  uvicorn app.main:app --reload
  ```
- После запуска сервера, документация API будет доступна по адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
</details>

<details><summary><h1>Запуск проекта через докер</h1></summary>

- Тут будет инструкция по сборке проекта через докер
</details>

# Авторы
[Сергей](https://github.com/Conqerorior)

[Иван](https://github.com/clownvkkaschenko)