FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY alembic alembic
COPY app app
COPY alembic.ini .
COPY load_data.py .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]