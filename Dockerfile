FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingestion/ ./ingestion/
COPY storage/ ./storage/
COPY ml/ ./ml/
COPY api/ ./api/
COPY orchestration/ ./orchestration/

ENV PYTHONPATH=/app
ENV WAREHOUSE_PATH=/data/warehouse

RUN mkdir -p /data/warehouse /tmp/dlq /tmp/watermarks /tmp/airflow/logs

CMD ["python3", "-m", "ingestion.pipeline"]