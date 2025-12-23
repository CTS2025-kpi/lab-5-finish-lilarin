FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./microservices/mcp_server/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./microservices /app/microservices

ENV PYTHONPATH=/app

CMD ["python", "microservices/mcp_server/main.py"]
