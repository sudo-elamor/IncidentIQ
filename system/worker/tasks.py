from celery_app import celery_app
from db.session import SessionLocal
from db.models.raw_logs import RawLog
from datetime import datetime
from utils.logger import get_logger

from metrics import (
    task_received_total,
    task_succeeded_total,
    task_failed_total,
    task_retried_total,
    task_processing_seconds,
)

AGENT_TASK_NAME = "incidentiq.agent.process_log"

logger = get_logger("Worker Tasks")


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
            logger.info("Processing payload: %s", payload)

            raw = payload.get("raw_log", {})
            logs = raw.get("logs", [])
            raw_log_ids = []

            # -----------------------------
            # Persist raw logs
            # -----------------------------
            with SessionLocal() as db:
                for entry in logs:
                    print("\n\n\nEntry:", entry, "\n\n\n")
                    message = (
                        entry.get("message")
                        or entry.get("metadata", {}).get("content")
                        or ""
                    )

                    log = RawLog(
                        timestamp=entry.get("timestamp") or datetime.now(),
                        source=raw.get("source", "unknown"),
                        host=raw.get("host", "unknown"),
                        service=entry.get("service") or "unknown",
                        level=entry.get("level", "unknown"),
                        message=message,
                        meta=entry.get("metadata", {}),
                    )
                    print("processed logs to be added to db:", log.__dict__)

                    db.add(log)
                    db.flush()   # assign ID without commit
                    raw_log_ids.append(log.id)

                db.commit()

            # -----------------------------
            # Fan-out to agent
            # -----------------------------
            for log_id in raw_log_ids:
                celery_app.send_task(
                    AGENT_TASK_NAME,
                    args=[{
                        "raw_log_id": log_id,
                        "source": raw.get("source", "unknown"),
                        "host": raw.get("host", "unknown"),
                        "logs": logs,
                    }],
                    queue="agent_queue",
                )

            task_succeeded_total.inc()
            return {"status": "processed", "count": len(raw_log_ids)}

        except Exception as exc:
            task_failed_total.inc()

            if self.request.retries < self.max_retries:
                task_retried_total.inc()
                raise

            celery_app.send_task(
                "incidentiq.dlq_log",
                args=[payload, str(exc)],
                queue="dlq",
            )
            raise
