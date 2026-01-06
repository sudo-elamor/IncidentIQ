import os
from prometheus_client import (
    Counter,
    Histogram,
    start_http_server,
    CollectorRegistry,
    multiprocess,
)

PROM_PORT = int(os.getenv("PROMETHEUS_PORT", "8001"))

def start_metrics_server():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(PROM_PORT, registry=registry)
    print(f"📊 Worker metrics on port {PROM_PORT}")


# Worker Metrics
task_received_total = Counter(
    "incidentiq_task_received_total",
    "Total Celery tasks received by worker"
)

task_succeeded_total = Counter(
    "incidentiq_task_succeeded_total",
    "Total Celery tasks succeeded"
)

task_failed_total = Counter(
    "incidentiq_task_failed_total",
    "Total Celery tasks failed"
)

task_retried_total = Counter(
    "incidentiq_task_retried_total",
    "Total Celery task retries"
)

task_processing_seconds = Histogram(
    "incidentiq_task_processing_seconds",
    "Time taken to process Celery tasks"
)

dlq_total = Counter(
    "incidentiq_dlq_total",
    "Total number of messages sent to DLQ"
)