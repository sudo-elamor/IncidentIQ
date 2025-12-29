from fastapi import FastAPI # type: ignore

from app.api.health import router as health_router
from app.api.logs import router as logs_router

app = FastAPI(
    title="IncidentIQ API",
    description="API for IncidentIQ system",
    version="1.0.0"
)

app.include_router(health_router, prefix="/health")
app.include_router(logs_router, prefix="/logs")
