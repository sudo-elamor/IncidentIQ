from celery import Celery

celery_app = Celery(
    "incidentiq",
    broker="redis://broker:6379/0",
    backend="redis://broker:6379/1"
)