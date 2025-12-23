FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY ai_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/microservices/libs
COPY ai_service /app/microservices/ai_service

CMD ["uvicorn", "microservices.ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
