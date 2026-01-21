from prometheus_client import Gauge

queue_depth = Gauge(
    "incidentiq_redis_queue_depth",
    "Number of messages in Redis queue",
    ["queue"]
)

queue_oldest_age = Gauge(
    "incidentiq_redis_queue_oldest_message_age_seconds",
    "Age of the oldest message in Redis queue",
    ["queue"]
)
