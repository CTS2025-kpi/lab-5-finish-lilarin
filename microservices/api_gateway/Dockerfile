FROM python:3.10-slim

WORKDIR /app

COPY api_gateway/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY libs /app/microservices/libs

COPY api_gateway /app/microservices/api_gateway

ENV PYTHONPATH=/app

WORKDIR /app/microservices/api_gateway

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]