# metrics_server.py
from prometheus_client import start_http_server, CollectorRegistry, multiprocess
import os

def start_metrics_server():
    port = int(os.getenv("PROMETHEUS_PORT", "8001"))
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(port, registry=registry)
    print(f"📊 Worker metrics running on {port}")
