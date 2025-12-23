FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY collections_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/microservices/libs
COPY collections_service /app/microservices/collections_service

ENV PYTHONPATH=/app

WORKDIR /app/microservices/collections_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]