FROM python:3.10-slim

WORKDIR /app

COPY router_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/microservices/libs
COPY router_service /app/microservices/router_service

ENV PYTHONPATH=/app

WORKDIR /app/microservices/router_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]