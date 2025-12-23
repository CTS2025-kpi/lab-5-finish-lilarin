FROM python:3.10-slim

WORKDIR /app

COPY shard_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/microservices/libs
COPY shard_service /app/microservices/shard_service

ENV PYTHONPATH=/app

WORKDIR /app/microservices/shard_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]