FROM python:3.10-slim

WORKDIR /app

COPY tags_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/microservices/libs
COPY tags_service /app/microservices/tags_service

ENV PYTHONPATH=/app

WORKDIR /app/microservices/tags_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]