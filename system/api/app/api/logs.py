from fastapi import APIRouter, HTTPException # type: ignore

from app.schemas.logs import LogIngestRequest
from app.utils.logger import get_logger
from app.api.services.celery_client import celery_app
from uuid import uuid4

from app.api.services.metrics import logs_ingested_total, logs_enqueued_total

logger = get_logger("API Service Logs")

router = APIRouter()

@router.post("/ingest",tags=["logs"])
def ingest_logs(payload: LogIngestRequest):

    if not payload:
        raise HTTPException(status_code=400, detail="No logs to ingest")
    
    logs_ingested_total.inc()
    
    #ingest in Kafka or RabbitMQ here( will add this)

    logger.info(f"Ingested logs from source {payload.source} at host {payload.host}")

    request_id = str(uuid4())

    celery_app.send_task(
        "incidentiq.process_log",
        args=[{
            request_id: request_id,
            "raw_log": payload.dict()
        }]
    )

    logs_enqueued_total.inc()

    return {
        "status" : "accepted",
        "request_id": request_id
    }
