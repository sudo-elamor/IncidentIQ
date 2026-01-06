FROM python:3.11-slim

WORKDIR /agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

WORKDIR /agent/app


CMD ["sh", "-c", "celery -A celery_app worker -Q agent_queue -l info"]
