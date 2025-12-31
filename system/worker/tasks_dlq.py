from celery_app import celery_app
from metrics import dlq_total

@celery_app.task(name="incidentiq.dlq_log")
def dlq_log(payload: dict, reason: str):
    dlq_total.inc()

    return {"dlq": "sent_to_dlq", "reason": reason}