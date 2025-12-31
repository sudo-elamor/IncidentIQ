from celery_app import celery_app
from metrics import (
    task_received_total,
    task_succeeded_total,
    task_failed_total,
    task_retried_total,
    task_processing_seconds,
    )

@celery_app.task(
    name="incidentiq.process_log",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_log(self, payload: dict):
    task_received_total.inc()

    with task_processing_seconds.time():
        try:
            if "CORRUPTED" in str(payload):
                raise ValueError("Bad log")

            task_succeeded_total.inc()
            return {"success": "processed"}

        except Exception as exc:
            task_failed_total.inc()

            if self.request.retries < self.max_retries:
                task_retried_total.inc()
                raise

            celery_app.send_task(
                "incidentiq.dlq_log",
                args = [payload, str(exc)],
                queue="dlq",
            )

            raise
