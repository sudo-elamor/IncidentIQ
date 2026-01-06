from prometheus_client import Counter, Histogram

# API Metrics
logs_ingested_total = Counter(
    "incidentiq_logs_ingested_total",
    "Total number of logs ingested"
)

logs_enqueued_total = Counter(
    "incidentiq_logs_enqueued_total",
    "Total Celery task enqueued"
)