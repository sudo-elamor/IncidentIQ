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
    """
    Payload format:
    {
        "request_id": "<uuid>",
        "raw_log": {
            "source": "...",
            "host": "...",
            "logs": [...]
        }
    }
    """

    task_received_total.inc()

    with task_processing_seconds.time():
        try:
            logger.info("Processing payload: %s", payload)

            raw = payload.get("raw_log", {})
            request_id = payload.get("request_id")
            logs = raw.get("logs", [])

            if not logs:
                logger.warning("No logs found in payload")
                return

            raw_log_ids = []

            # ---- Persist raw logs ----
            with SessionLocal() as db:
                for entry in logs:
                    # 🔑 Message normalization (critical)
                    message = (
                        entry.get("message")
                        or entry.get("metadata", {}).get("content")
                        or ""
                    )

                    log = RawLog(
                        timestamp=datetime.fromisoformat(
                            entry.get("timestamp").replace("Z", "+00:00")
                        ) if entry.get("timestamp") else datetime.utcnow(),
                        source=raw.get("source", "unknown"),
                        host=raw.get("host", "unknown"),
                        service=entry.get("service") or "unknown",
                        level=entry.get("level", "unknown"),
                        message=message,
                        meta=entry.get("metadata", {}),
                    )

                    db.add(log)
                    db.flush()          # assigns ID
                    raw_log_ids.append(log.id)

                db.commit()

            logger.info(
                "Inserted %d raw logs | request_id=%s",
                len(raw_log_ids),
                request_id,
            )

            # ---- Send ONLY identifiers to agent ----
            celery_app.send_task(
                AGENT_TASK_NAME,
                args=[{
                    "request_id": request_id,
                    "raw_log_ids": raw_log_ids,
                    "source": raw.get("source", "unknown"),
                    "host": raw.get("host", "unknown"),
                }],
                queue="agent_queue",
            )

            task_succeeded_total.inc()
            return {"status": "processed", "count": len(raw_log_ids)}

        except Exception as exc:
            task_failed_total.inc()
            logger.exception("Worker failed: %s", exc)

            if self.request.retries < self.max_retries:
                task_retried_total.inc()
                raise

            # ---- DLQ ----
            celery_app.send_task(
                "incidentiq.dlq_log",
                args=[payload, str(exc)],
                queue="dlq",
            )

            raise
