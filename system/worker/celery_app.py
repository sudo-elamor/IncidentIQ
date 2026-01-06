from celery import Celery
from kombu import Queue
from celery.signals import worker_process_init
from metrics_server import start_metrics_server
from celery.signals import worker_ready



celery_app = Celery(
    "incidentiq",
    broker="redis://broker:6379/0",
    backend="redis://broker:6379/1",
    include=["tasks","tasks_dlq"]
)


@worker_ready.connect
def start_metrics_once(sender=None, **kwargs):
    start_metrics_server()

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    task_acks_late=True,            # Acks only after success
    worker_prefetch_multiplier=1,   # one task at a time per worker
    task_reject_on_worker_lost=True,  # Re-queue tasks if worker crashes/ Crash Safety

    task_queues = (
    Queue("celery"),
    Queue("dlq"),
    ),

    task_default_queue = "celery",


    broker_transport_options={
        "visibility_timeout": 3600, # 1 hour
    }
)