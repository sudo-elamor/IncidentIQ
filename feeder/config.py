LOGS_PER_SECOND = 1
LATENCY_MS_MIN = 0
LATENCY_MS_MAX = 100
LOG_FILE = "logs/feeder.log"

import os

LOG_MODE = os.getenv("LOG_MODE", "stdout")
HTTP_ENDPOINT = os.getenv("HTTP_ENDPOINT", "http://localhost:8000/logs/ingest")
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "5"))
