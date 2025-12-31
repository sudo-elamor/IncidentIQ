FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /tmp/prometheus && chmod 777 /tmp/prometheus
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus


COPY . .

EXPOSE 8001

#EXPORT PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus

CMD ["sh", "-c", "python metrics_server.py & celery -A celery_app worker -Q celery,dlq -l info"]