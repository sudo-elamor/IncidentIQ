from fastapi import APIRouter, HTTPException # type: ignore

from app.schemas.logs import LogIngestRequest
from app.utils.logger import get_logger

logger = get_logger("API Service Logs")

router = APIRouter()

@router.post("/ingest",tags=["logs"])
def ingest_logs(payload: LogIngestRequest):

    if not payload:
        raise HTTPException(status_code=400, detail="No logs to ingest")
    
    #ingest in Kafka or RabbitMQ here( will add this)

    logger.info(f"Ingested logs from source {payload.source} at host {payload.host}")

    return {
        "status" : "accepted",
        "source" : payload.source
    }
